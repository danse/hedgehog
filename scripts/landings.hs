#!/usr/bin/env -S runghc -package=directory -package=filepath
-- | Count landing markers across the Tidal tracks and print a grouped table.
-- A landing is a double blank line between two non-blank paragraphs, per
-- AGENTS.md. Lines are classified with ReadP combinators, so the same parser
-- can later pick out TODO and Workaround comments. Run from the repo root.
module Main (main) where

import Control.Monad (filterM)
import Data.Char (isAlpha)
import Data.List (intercalate, nub, sort, tails)
import System.Directory (doesDirectoryExist, listDirectory)
import System.FilePath ((</>), takeBaseName, takeExtension)
import Text.ParserCombinators.ReadP (ReadP, eof, munch, munch1, readP_to_S,
                                     skipSpaces, string, (<++))

data Line = Blank | Todo String | Workaround String | Other String
  deriving (Eq, Show)

main :: IO ()
main = do
  paths <- tidalFiles "tracks"
  counts <- mapM countFile paths
  let levels = reverse (sort (nub (map fst counts)))
  putStrLn "| Landings | Tracks |"
  putStrLn "|---:|---|"
  mapM_ (printRow counts) levels

tidalFiles :: FilePath -> IO [FilePath]
tidalFiles dir = do
  entries <- sort <$> listDirectory dir
  let paths = map (dir </>) entries
  dirs <- filterM doesDirectoryExist paths
  nested <- concat <$> mapM tidalFiles dirs
  pure (nested ++ [p | p <- paths, takeExtension p == ".tidal"])

countFile :: FilePath -> IO (Int, String)
countFile path = do
  text <- readFile path
  pure (landings (map parseLine (lines text)), takeBaseName path)

-- Classify one line. TODO and Workaround are recognised here rather than in
-- the landing rule, so markers can be added to the report later.
parseLine :: String -> Line
parseLine s = case readP_to_S (lineP <* eof) s of
  ((line, _):_) -> line
  [] -> Other s

lineP :: ReadP Line
lineP = blankP <++ commentP <++ otherP

blankP :: ReadP Line
blankP = skipSpaces >> eof >> pure Blank

commentP :: ReadP Line
commentP = do
  skipSpaces
  _ <- string "--"
  skipSpaces
  word <- munch1 isAlpha
  rest <- munch (const True)
  pure $ case word of
    "TODO" -> Todo rest
    "Workaround" -> Workaround rest
    _ -> Other (word ++ rest)

otherP :: ReadP Line
otherP = Other <$> munch (const True)

landings :: [Line] -> Int
landings ls = length
  [ () | (a:b:c:d:_) <- tails ls
       , isText a, isBlank b, isBlank c, isText d ]
  where
    isBlank Blank = True
    isBlank _ = False
    isText = not . isBlank

printRow :: [(Int, String)] -> Int -> IO ()
printRow counts level =
  let names = sort [name | (n, name) <- counts, n == level]
      cells = intercalate ", " (map (\s -> "`" ++ s ++ "`") names)
  in putStrLn ("| " ++ show level ++ " | " ++ cells ++ " |")
