-- Expose tidal-core so the chord helpers are importable.
:set -package tidal-core
:set -fno-warn-orphans -Wno-type-defaults -XMultiParamTypeClasses -XOverloadedStrings
:set prompt ""

-- Import all the boot functions and aliases.
import Sound.Tidal.Boot

-- Tidal Chords (e.g. chord "d4" "min7" []).
import Sound.Tidal.Chords

-- Concurrency, for gentle tempo changes (glideBpm).
import Control.Concurrent (forkIO, threadDelay)

default (Rational, Integer, Double, Pattern String)

-- Create a Tidal Stream with the default settings.
-- To customize these settings, use 'mkTidalWith' instead
tidalInst <- mkTidal

-- tidalInst <- mkTidalWith [(superdirtTarget { oLatency = 0.01 }, [superdirtShape])] (defaultConfig {cFrameTimespan = 1/50, cProcessAhead = 1/20})

-- This orphan instance makes the boot aliases work!
-- It has to go after you define 'tidalInst'.
instance Tidally where tidal = tidalInst

-- `enableLink` and `disableLink` can be used to toggle synchronisation using the Link protocol.
-- Uncomment the next line to enable Link on startup.
-- enableLink

-- --- gentle tempo changes ---------------------------------------------------
-- `setbpm` jumps the clock instantly. `glideBpm target secs` walks it there in
-- small steps over `secs` seconds (10 steps/s). It forks, so the sender is not
-- blocked. Each glide starts from the tempo current when it is called.
:{
let glideBpm :: Double -> Double -> IO ()
    glideBpm target secs = do
      start <- getbpm
      let s = fromRational start :: Double
          n = max 20 (round (secs * 10) :: Int)
          step = (target - s) / fromIntegral n
          pause = round (secs * 1000000 / fromIntegral n) :: Int
      _ <- forkIO $
        mapM_
          (\i -> do
            setbpm (realToFrac (s + step * fromIntegral i))
            threadDelay pause)
          [1 .. n]
      pure ()
:}

-- You can also add your own aliases in this file. For example:
-- fastsquizzed pat = fast 2 $ pat # squiz 1.5

:set prompt "tidal> "
:set prompt-cont ""
