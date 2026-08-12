import { useState } from "react";
import Onboarding from "./Onboarding";
import Chat from "./Chat";

function App() {
  const [profile, setProfile] = useState(null);

  return (
    <div>
      {profile ? (
        <Chat profile={profile} />
      ) : (
        <Onboarding onComplete={setProfile} />
      )}
    </div>
  );
}

export default App;