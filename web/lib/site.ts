export const site = {
  name: "Liberty Lawn Care",
  phone: "(630) 538-1787",
  phoneHref: "tel:+16305381787",
  tagline: "Reliable, family-run lawn care in Batavia and the Fox Valley.",
  serviceArea: "Batavia, Illinois and the surrounding area",
  areas: [
    "Batavia",
    "Geneva",
    "St. Charles",
    "Campton Hills",
    "Wayne",
    "Oswego",
    "Aurora",
  ],
  nav: [
    { label: "Services", href: "/#services" },
    { label: "About", href: "/#about" },
    { label: "Reviews", href: "/#reviews" },
    { label: "Leave a Review", href: "/reviews/new" },
  ],
  images: {
    band: "/images/band.png",
    about: ["/images/about-1.png", "/images/about-2.jpg"],
  },
  services: [
    {
      name: "Lawn Mowing",
      description: "Clean, consistent cuts on a schedule that fits your lawn.",
      image: "/images/services/mowing.jpg",
    },
    {
      name: "Core Aeration",
      description:
        "Relieves compacted soil so water and nutrients reach the roots.",
      image: "/images/services/aeration.jpeg",
    },
    {
      name: "Seasonal Cleanups",
      description: "Leaves, debris, and beds cleared in spring and fall.",
      image: "/images/services/cleanups.jpg",
    },
    {
      name: "Mulching",
      description: "Fresh mulch that keeps beds tidy and holds in moisture.",
      image: "/images/services/mulching.png",
    },
    {
      name: "Hedge & Shrub Trimming",
      description: "Shaped and trimmed for a sharp, healthy look.",
      image: "/images/services/trimming.webp",
    },
    {
      name: "Fertilization",
      description: "Feeding programs for a thicker, greener lawn.",
      image: "/images/services/fertilization.jpg",
    },
  ],
} as const;
