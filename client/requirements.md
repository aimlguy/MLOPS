## Packages
recharts | Data visualization for dashboard metrics
date-fns | Date formatting for tables and charts
framer-motion | Smooth page transitions and UI animations
clsx | Utility for conditional class names (often used with tailwind-merge)
tailwind-merge | Utility for merging tailwind classes

## Notes
Tailwind Config - extend fontFamily:
fontFamily: {
  sans: ["Inter", "sans-serif"],
  mono: ["JetBrains Mono", "monospace"],
}
API expects dates as ISO strings.
Backend might be simulated, handle 404s/mock data if endpoints aren't ready.
