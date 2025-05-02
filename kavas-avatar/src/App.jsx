import { useState, useCallback } from "react";
import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";
import UI from "./components/UI"; // Now memoized

function App() {
  const [audioData, setAudioData] = useState({
    audioUrl: null,
    lipsyncData: null,
  });
  const [isTalking, setIsTalking] = useState(false);
  const [isGreeting, setIsGreeting] = useState(false);

  // Memoized function to prevent unnecessary re-renders
  const handleAudioReceived = useCallback(
    (audioUrl, lipsyncData, isGreeting) => {
      setAudioData({ audioUrl, lipsyncData });
      console.log("I am being called");
      setIsTalking(true);
      setIsGreeting(isGreeting);
    },
    []
  );

  const handleAvatarFinishedTalking = useCallback(() => {
    setIsTalking(false);
    setIsGreeting(false);
    setAudioData({
      audioUrl: null,
      lipsyncData: null,
    });
    console.log("should stop talking again with the same voice");
  }, []);

  return (
    <>
      <Canvas shadows>
        <color attach="background" args={["#ececec"]} />
        <Experience
          audioData={audioData}
          onAvatarFinishedTalking={handleAvatarFinishedTalking}
          isTalking={isTalking}
          isGreeting={isGreeting}
        />
      </Canvas>
      <UI onAudioReceived={handleAudioReceived} isTalking={isTalking} />
    </>
  );
}

export default App;
