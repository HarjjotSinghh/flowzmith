import Image from "next/image"

export function DashboardPreview() {
  return (
    <div className="w-full">
      <div className="rounded-3xl border border-border/70 bg-card/85 p-3 shadow-lg">
        <Image
          src="/images/flow-hero.jpg"
          alt="Dashboard preview"
          width={1160}
          height={700}
          className="w-full h-full object-cover rounded-2xl"
        />
      </div>
    </div>
  )
}
