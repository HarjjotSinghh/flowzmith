"use client";

import Hyperspeed, { hyperspeedPresets } from "./HyperSpeed";

const preset = hyperspeedPresets.one; // Or load dynamic preset logic here

export default function HyperspeedWrapper() {

  // Define your client-side interactive functions here.
  // These could be state setters, analytics calls, etc.
  const handleSpeedUp = (ev) => {
    console.log("Speed up started on the client!");
    // You can call your original onSpeedUp logic here
  };

  const handleSlowDown = (ev) => {
    console.log("Slow down stopped on the client!");
    // You can call your original onSlowDown logic here
  };

  return (
    <div className="w-full min-h-screen relative">
      <div className="absolute -top-[8vh] -left-[13vw] w-full h-full z-10">
        <Hyperspeed
        effectOptions={preset}
        onSpeedUp={handleSpeedUp}
        onSlowDown={handleSlowDown}
      />
      </div>
    </div>
  );
}
