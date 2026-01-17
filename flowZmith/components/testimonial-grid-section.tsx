import Image from "next/image"

const testimonials = [
  {
    quote:
      "Flowzmith feels like having a senior reviewer embedded in our editor. We ship faster with fewer regressions.",
    name: "Annette Black",
    company: "Sony",
    avatar: "/images/avatars/annette-black.png",
  },
  {
    quote: "The MCP server connections saved us days of configuration work.",
    name: "Dianne Russell",
    company: "McDonald's",
    avatar: "/images/avatars/dianne-russell.png",
  },
  {
    quote:
      "The multi-agent coding flow helped us resolve complex bugs in hours instead of weeks.",
    name: "Cameron Williamson",
    company: "IBM",
    avatar: "/images/avatars/cameron-williamson.png",
  },
  {
    quote: "Flowzmith brought our integrations together in one place and simplified the workflow.",
    name: "Robert Fox",
    company: "MasterCard",
    avatar: "/images/avatars/robert-fox.png",
  },
  {
    quote: "We upgraded to Pro in the first week. It quickly became part of our core stack.",
    name: "Darlene Robertson",
    company: "Ferrari",
    avatar: "/images/avatars/darlene-robertson.png",
  },
  {
    quote:
      "Real-time previews made pair programming more productive and significantly faster.",
    name: "Cody Fisher",
    company: "Apple",
    avatar: "/images/avatars/cody-fisher.png",
  },
]

export function TestimonialGridSection() {
  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
            Coding made effortless
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Hear how teams build faster, collaborate seamlessly, and ship with confidence using Flowzmith.
          </p>
        </div>
        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((item) => (
            <div key={item.name} className="rounded-2xl border border-border/70 bg-card/80 p-6">
              <p className="text-sm text-muted-foreground">{item.quote}</p>
              <div className="mt-6 flex items-center gap-3">
                <Image
                  src={item.avatar}
                  alt={`${item.name} avatar`}
                  width={44}
                  height={44}
                  className="h-11 w-11 rounded-full border border-border"
                />
                <div>
                  <div className="text-sm font-semibold text-foreground">{item.name}</div>
                  <div className="text-xs text-muted-foreground">{item.company}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
