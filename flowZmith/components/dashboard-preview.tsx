import Image from "next/image"

export function DashboardPreview() {
  return (
    <div className="w-full">
      <div className="border-4 border-t-0 border-foreground bg-background p-0 relative">
        <div className="absolute top-0 right-0 bg-accent text-black font-black px-4 py-1 text-[10px] uppercase tracking-widest z-10">
          SYSTEM_PREVIEW_V1.0
        </div>
        <div className="border-2 border-foreground overflow-hidden">
          <Image
            src="/images/flow-hero.jpg"
            alt="Dashboard preview"
            width={1160}
            height={700}
            className="w-full h-auto grayscale hover:grayscale-0 transition-all duration-700"
          />
        </div>
        <div className="flex justify-between items-center mt-2 px-2 text-[8px] font-black text-foreground/80 uppercase">
          <span>FRAME_ID: 0x99283-Z</span>
          <span>COMPRESSION: NONE</span>
          <span>RESOLUTION: 4K_NATIVE</span>
        </div>
      </div>
    </div>
  )
}