import { cva } from 'class-variance-authority'

export const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ocean-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-ocean-600 text-white hover:bg-ocean-700 shadow-ocean-sm hover:shadow-ocean-md',
        ocean: 'bg-ocean-600 text-white hover:bg-ocean-700 shadow-ocean-sm hover:shadow-ocean-md',
        wave: 'bg-wave-500 text-white hover:bg-wave-600 shadow-ocean-sm hover:shadow-ocean-md',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
        outline: 'border-2 border-ocean-300 bg-white hover:bg-ocean-50 text-ocean-700',
        secondary: 'bg-foam-200 text-foam-900 hover:bg-foam-300',
        ghost: 'hover:bg-ocean-50 hover:text-ocean-700 text-foam-700',
        link: 'text-ocean-600 underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3 text-xs',
        lg: 'h-12 rounded-lg px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)
