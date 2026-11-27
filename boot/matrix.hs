-- Matrix (grid) affordances for Hedgehog tracks.
--
-- Sourced by `boot/BootTidal.hs` with `:script`, not imported as a module. It
-- relies on the imports and shared helpers already in the boot script:
-- `ControlPattern`, `ID`, `Map`, `p`, `putStrLn` and `hFlush`.
--
-- The interface rule: the matrix chooses *what*, the transition chooses *how*.
-- A named voice call returns a ControlPattern, so the live coder puts it under
-- a straight attack (`p`/`attacks`), a clutch (`clutchIn`) or a fade
-- (`xfadeIn`). No transition is hidden inside the voice call.
--
-- A `Movement` is one cell: `Silent`, a required `Score`, or an `Optional` score
-- the live coder may bring in. Entering a row mutes every named seat it does
-- not score with the same transition that brings the scores in; an omitted
-- seat counts as silent too.
-- A `MovementRow` is one movement: seat -> cell,
-- with a descriptive label and voice names so commands can talk in voices
-- rather than stream numbers. `Movements` bundles rows by those labels for
-- tooling; the live names are local bindings chosen by each track.
--
-- Typical setup:
--   kotoVoice p = swing8 $ note p # s "hedge_koto" ...
--   koto = mkVoice 12 "koto"
--   opening = mkMovement "opening" [(12, "koto")]
--                       [(12, Optional (kotoVoice "c5 ..."))]
-- Then:
--   p 12 (koto opening)                   -- straight attack
--   clutchIn 12 8 (koto opening)          -- clutch
--   xfadeIn 12 8 (koto opening)           -- fade
--   multi clutchIn 16 [(4, koto opening)] -- explicit group

import Debug.Trace (trace)

:{

data Movement = Silent | Score ControlPattern | Optional ControlPattern

data MovementRow = MovementRow
  { rowLabel :: String
  , rowNames :: Map.Map ID String
  , rowCells :: Map.Map ID Movement
  }

newtype Movements = Movements (Map.Map String MovementRow)

:}

:{
let
  -- Build a row from seat/name and seat/cell pairs.
  mkMovement :: String -> [(ID, String)] -> [(ID, Movement)] -> MovementRow
  mkMovement label names cells =
    MovementRow label (Map.fromList names) (Map.fromList cells)
  --
  -- Bundle rows by their own descriptive labels. Live calls use the local
  -- bindings, not this map.
  mkMovements :: [MovementRow] -> Movements
  mkMovements = Movements . Map.fromList . map (\mv -> (rowLabel mv, mv))
  --
  -- ID is a string newtype, so Map.toList orders 1, 12, 2. Read the seat
  -- number once; listings and groups all use this order.
  seatOrder :: ID -> Maybe Int
  seatOrder = readMaybe . fromID
  --
  orderedCells :: MovementRow -> [(ID, Movement)]
  orderedCells = sortOn (seatOrder . fst) . Map.toList . rowCells
  --
  -- Print and flush together, so a line appears before the fade starts.
  say :: String -> IO ()
  say s = putStrLn s >> hFlush stdout
  --
  -- Voice name for display, falling back to the seat for unnamed voices.
  nameWith :: String -> MovementRow -> ID -> String
  nameWith fallback mv seat =
    Map.findWithDefault (fallback ++ " " ++ fromID seat) seat (rowNames mv)
  --
  -- Named voice accessor. It is pure: Score and Optional return their score,
  -- Silent returns silence with a trace so the call reports itself when the
  -- pattern is demanded by p, clutchIn, xfadeIn or an introspection command.
  -- The seat is both the cell lookup key and the destination stream: pass the
  -- same ID to p/clutchIn/xfadeIn so a voice owns one dN across rows.
  mkVoice :: ID -> String -> MovementRow -> ControlPattern
  mkVoice seat name mv =
    case Map.lookup seat (rowCells mv) >>= playable of
      Just p -> p
      Nothing -> trace ("voice " ++ name ++ " silent in movement " ++ rowLabel mv)
                 silence
    where
      playable (Score p) = Just p
      playable (Optional p) = Just p
      playable Silent = Nothing
  --
  -- Straight attacks, grouped by seat. Pairs are (ID, ControlPattern).
  attacks :: [(ID, ControlPattern)] -> IO ()
  attacks = mapM_ (uncurry p)
  --
  -- Announce a row and its optionals, then hand every named seat back as a
  -- transition-ready pair: a Score brings its pattern; an Optional, Silent or
  -- omitted seat brings `silence`. So entering a row clears every voice it
  -- does not score, and a live `koto opening` can bring an optional back.
  -- mPlay chooses no fade:
  --   mPlay opening >>= multi clutchIn 16
  --   mPlay opening >>= multi xfadeIn 8
  --   mPlay opening >>= attacks
  mPlay :: MovementRow -> IO [(ID, ControlPattern)]
  mPlay mv = do
    say ("movement " ++ rowLabel mv)
    mOptionals mv
    pure
      [ (seat, maybe silence outcome (Map.lookup seat (rowCells mv)))
      | seat <- sortOn seatOrder (Map.keys (rowNames mv)) ]
    where
      outcome (Score p) = p
      outcome _ = silence
  --
  -- Show the voices a movement offers but does not play by default.
  mOptionals :: MovementRow -> IO ()
  mOptionals mv = do
    if null opts
      then say ("no optionals in movement " ++ rowLabel mv)
      else do
        say ("optionals in movement " ++ rowLabel mv ++ ":")
        mapM_ say
          ["  " ++ fromID seat ++ "  " ++ nameWith "voice" mv seat
          | seat <- opts]
    where
      opts = [seat | (seat, Optional _) <- orderedCells mv]
  --
  -- Full row, including silences; useful when learning a new grid.
  mShow :: MovementRow -> IO ()
  mShow mv = do
    say ("movement " ++ rowLabel mv)
    mapM_ say
      [ "  " ++ fromID seat ++ "  " ++ nameWith "seat" mv seat ++ "  " ++ state cell
      | (seat, cell) <- orderedCells mv ]
    where
      state Silent = "silent"
      state (Score _) = "score"
      state (Optional _) = "optional"
:}
