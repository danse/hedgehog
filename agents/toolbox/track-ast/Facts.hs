{-# LANGUAGE ScopedTypeVariables #-}
module Main where

import GHC.Parser (parseDeclaration, parseStmt)
import GHC.Parser.Lexer (ParserOpts, initParserState, mkParserOpts,
                         ParseResult(..), unP)
import GHC.Data.StringBuffer (stringToStringBuffer)
import GHC.Types.SrcLoc (mkRealSrcLoc, noLoc, unLoc, GenLocated(L))
import GHC.Data.FastString (fsLit, unpackFS)
import GHC.Data.EnumSet (empty)
import GHC.Utils.Error (emptyDiagOpts)
import GHC.Utils.Outputable (showSDocUnsafe, ppr)
import GHC.Data.Bag (bagToList)
import GHC.Types.SourceText (IntegralLit(il_value))
import GHC.Types.Name.Reader (RdrName, rdrNameOcc)
import GHC.Types.Name.Occurrence (occNameString)
import GHC.Hs
import Language.Haskell.Syntax.Expr
  (HsExpr(..), Stmt(..), HsTupArg(..), Match(..), MatchGroup(..),
   GRHSs(..), GRHS(..))
import Language.Haskell.Syntax.Binds
  (HsBindLR(..), HsLocalBindsLR(..), HsValBindsLR(..))
import Language.Haskell.Syntax.Lit (HsLit(..), OverLitVal(..), HsOverLit(..))
import Language.Haskell.Syntax.Pat (Pat(..), HsFieldBind(..), rec_flds)
import Language.Haskell.Syntax.Type (FieldOcc(..))
import Language.Haskell.Syntax.Decls (HsDecl(..))
import Data.Char (isControl, ord)
import Numeric (showHex)

opts :: ParserOpts
opts = mkParserOpts empty emptyDiagOpts [] False False False False

main :: IO ()
main = do
  input <- getContents
  mapM_ parseGroup (pairsOf (splitNul input))

parseGroup :: (String, String) -> IO ()
parseGroup (lineno, text) = do
  let state = initParserState opts (stringToStringBuffer text)
                               (mkRealSrcLoc (fsLit "<track>") (read lineno) 1)
  let declFacts decl = map (bindFact lineno) (declBinds (unLoc decl))
      tryStmt reportFailure = case unP parseStmt state of
        POk _ (Just stmt) -> mapM_ putStrLn (stmtFacts lineno (unLoc stmt))
        POk _ Nothing -> pure ()
        PFailed _ -> if reportFailure
          then putStrLn (lineno ++ " ERROR " ++ quote (unwords (words text)))
          else pure ()
  case unP parseDeclaration state of
    POk _ decl -> mapM_ putStrLn (declFacts decl) >> tryStmt False
    PFailed _ -> tryStmt True

stmtFacts :: String -> Stmt GhcPs (LHsExpr GhcPs) -> [String]
stmtFacts lineno stmt = case stmt of
  BodyStmt _ expr _ _ -> [lineno ++ " STMT " ++ sexprExpr expr]
  LetStmt _ binds -> map (bindFact lineno) (bindsFields binds)
  LastStmt _ expr _ _ -> [lineno ++ " STMT " ++ sexprExpr expr]
  BindStmt _ _pat expr -> [lineno ++ " STMT " ++ sexprExpr expr]
  _ -> []

bindFact :: String -> (String, [String], String) -> String
bindFact lineno fields = lineno ++ " BIND " ++ bindSexpr fields

bindSexpr :: (String, [String], String) -> String
bindSexpr (name, pats, body) =
  "(" ++ unwords [quote name, patsSexpr pats, body] ++ ")"

patsSexpr :: [String] -> String
patsSexpr pats = "(" ++ unwords pats ++ ")"

bindsFields :: HsLocalBinds GhcPs -> [(String, [String], String)]
bindsFields binds = case binds of
  HsValBinds _ (ValBinds _ bs _) -> map (bindFields . unLoc) (bagToList bs)
  EmptyLocalBinds _ -> []
  _ -> []

bindsFacts :: HsLocalBinds GhcPs -> [String]
bindsFacts = map bindSexpr . bindsFields

declBinds :: HsDecl GhcPs -> [(String, [String], String)]
declBinds decl = case decl of
  ValD _ bind -> [bindFields bind]
  _ -> []

bindFields :: HsBind GhcPs -> (String, [String], String)
bindFields bind = case bind of
  FunBind { fun_id = name, fun_matches = matches } ->
    case firstMatch matches of
      Just m -> (nameOf name, map patField (m_pats m),
                 maybe (unsupported "no rhs") sexpr (matchBody m))
      Nothing -> (nameOf name, [], unsupported "no match")
  PatBind { pat_lhs = pat, pat_rhs = rhs } ->
    (patLabel pat, [], maybe (unsupported "no rhs") sexpr (firstRhsBody rhs))
  _ -> ("?", [], unsupported "bind")

patField :: LPat GhcPs -> String
patField pat = case unLoc pat of
  VarPat _ name -> "(pvar " ++ quote (nameOf name) ++ ")"
  ParPat _ p -> patField p
  TuplePat _ ps _ -> "(ptuple " ++ unwords (map patField ps) ++ ")"
  WildPat _ -> "(pwild)"
  _ -> "(pany)"

patLabel :: LPat GhcPs -> String
patLabel pat = case unLoc pat of
  VarPat _ name -> nameOf name
  ParPat _ p -> patLabel p
  _ -> "?"

firstMatch :: MatchGroup GhcPs (LHsExpr GhcPs) -> Maybe (Match GhcPs (LHsExpr GhcPs))
firstMatch mg = case unLoc (mg_alts mg) of
  (m:_) -> Just (unLoc m)
  [] -> Nothing

matchBody :: Match GhcPs (LHsExpr GhcPs) -> Maybe (HsExpr GhcPs)
matchBody m = case grhssGRHSs (m_grhss m) of
  (g:_) -> rhsBody g
  [] -> Nothing

rhsBody :: LGRHS GhcPs (LHsExpr GhcPs) -> Maybe (HsExpr GhcPs)
rhsBody g = case unLoc g of
  GRHS _ _ body -> Just (unLoc body)

firstRhsBody :: GRHSs GhcPs (LHsExpr GhcPs) -> Maybe (HsExpr GhcPs)
firstRhsBody rhs = case grhssGRHSs rhs of
  (g:_) -> rhsBody g
  [] -> Nothing

nameOf :: LIdP GhcPs -> String
nameOf = occNameString . rdrNameOcc . unLoc

sexprExpr :: LHsExpr GhcPs -> String
sexprExpr (L _ expr) = sexpr expr

sexpr :: HsExpr GhcPs -> String
sexpr expr = case expr of
  HsVar _ name -> "(var " ++ quote (nameOf name) ++ ")"
  HsUnboundVar _ name -> "(var " ++ quote (occNameString (rdrNameOcc name)) ++ ")"
  HsOverLit _ lit -> case ol_val lit of
    HsIsString _ fs -> "(str " ++ quote (unpackFS fs) ++ ")"
    HsIntegral i -> "(num " ++ show (il_value i) ++ ")"
    HsFractional f -> "(num " ++ showSDocUnsafe (ppr f) ++ ")"
  HsLit _ lit -> case lit of
    HsString _ fs -> "(str " ++ quote (unpackFS fs) ++ ")"
    HsChar _ c -> "(str " ++ quote [c] ++ ")"
    HsInt _ i -> "(num " ++ show (il_value i) ++ ")"
    _ -> unsupported "literal"
  HsApp _ f a -> let (h, as) = apps expr
                 in "(app " ++ sexpr h ++ concatMap ((' ':) . sexprExpr) as ++ ")"
  OpApp _ l op r
    | opExprName op == "#" ->
        "(chain # " ++ unwords (map sexpr (opChain "#" expr)) ++ ")"
    | otherwise -> "(op " ++ quote (opExprName op) ++ " " ++ sexprExpr l ++ " "
                   ++ sexprExpr r ++ ")"
  NegApp _ a _ -> "(neg " ++ sexprExpr a ++ ")"
  HsPar _ a -> sexprExpr a
  SectionL _ a op -> "(sectionL " ++ sexprExpr a ++ " " ++ quote (opExprName op) ++ ")"
  SectionR _ op a -> "(sectionR " ++ quote (opExprName op) ++ " " ++ sexprExpr a ++ ")"
  ExplicitList _ xs -> "(list " ++ unwords (map sexprExpr xs) ++ ")"
  ExplicitTuple _ args _ -> "(tuple " ++ unwords (map tupArg args) ++ ")"
  HsLet _ binds body -> "(let (" ++ unwords (bindsFacts binds)
                        ++ ") " ++ sexprExpr body ++ ")"
  HsLam _ _ mg -> case firstMatch mg of
    Just m -> "(lam (" ++ unwords (map patField (m_pats m)) ++ ") "
              ++ maybe (unsupported "no rhs") sexpr (matchBody m) ++ ")"
    Nothing -> unsupported "lambda"
  ExprWithTySig _ a _ -> sexprExpr a
  RecordCon { rcon_con = con, rcon_flds = flds } ->
    "(record " ++ quote (nameOf con) ++ " ("
      ++ unwords (map recField (rec_flds flds)) ++ "))"
  ArithSeq {} -> unsupported "arithSeq"
  HsIf {} -> unsupported "if"
  HsCase {} -> unsupported "case"
  HsDo {} -> unsupported "do"
  _ -> unsupported "expr"

apps :: HsExpr GhcPs -> (HsExpr GhcPs, [LHsExpr GhcPs])
apps (HsApp _ f a) = let (h, as) = apps (unLoc f) in (h, as ++ [a])
apps e = (e, [])

opChain :: String -> HsExpr GhcPs -> [HsExpr GhcPs]
opChain op (OpApp _ l o r) | opExprName o == op =
  opChain op (unLoc l) ++ [unLoc r]
opChain _ e = [e]

opExprName :: LHsExpr GhcPs -> String
opExprName op = case unLoc op of
  HsVar _ name -> nameOf name
  other -> unwords (words (showSDocUnsafe (ppr other)))

tupArg :: HsTupArg GhcPs -> String
tupArg (Present _ e) = sexprExpr e
tupArg (Missing _) = "(missing)"

recField :: LHsRecField GhcPs (LHsExpr GhcPs) -> String
recField field =
  let bind = unLoc field
  in "(" ++ quote (fieldName (hfbLHS bind)) ++ " "
     ++ sexprExpr (hfbRHS bind) ++ ")"

fieldName :: LFieldOcc GhcPs -> String
fieldName loc = case unLoc loc of
  FieldOcc _ label -> occNameString (rdrNameOcc (unLoc label))

unsupported :: String -> String
unsupported what = "(unsupported " ++ quote what ++ ")"

quote :: String -> String
quote s = '"' : concatMap esc s ++ "\""
  where
    esc '"' = "\\\""
    esc '\\' = "\\\\"
    esc '\n' = "\\n"
    esc '\r' = "\\r"
    esc '\t' = "\\t"
    esc c | isControl c = "\\u" ++ replicate (4 - length h) '0' ++ h
          | otherwise = [c]
      where h = showHex (ord c) ""

splitNul :: String -> [String]
splitNul [] = []
splitNul s = let (a, rest) = break (== '\0') s
             in a : case rest of
               [] -> []
               (_:more) -> splitNul more

pairsOf :: [a] -> [(a, a)]
pairsOf (a:b:rest) = (a, b) : pairsOf rest
pairsOf _ = []
