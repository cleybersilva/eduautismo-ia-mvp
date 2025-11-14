import { forwardRef } from 'react'
import { clsx } from 'clsx'
import { Loader2 } from 'lucide-react'

const buttonVariants = {
  default: 'bg-gradient-to-r from-blue-400 to-blue-500 text-white hover:from-blue-500 hover:to-blue-600 shadow-md shadow-blue-200/50',
  destructive: 'bg-gradient-to-r from-red-400 to-red-500 text-white hover:from-red-500 hover:to-red-600 shadow-md shadow-red-200/50',
  outline: 'border-2 border-slate-200 bg-white hover:bg-slate-50 hover:border-slate-300 text-slate-700',
  secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
  ghost: 'hover:bg-slate-100 text-slate-700',
  link: 'text-blue-600 underline-offset-4 hover:underline',
  success: 'bg-gradient-to-r from-emerald-400 to-emerald-500 text-white hover:from-emerald-500 hover:to-emerald-600 shadow-md shadow-emerald-200/50',
}

const buttonSizes = {
  default: 'h-12 px-6 py-3 text-base',
  sm: 'h-10 px-4 py-2 text-sm',
  lg: 'h-14 px-8 py-4 text-lg',
  icon: 'h-12 w-12',
}

const Button = forwardRef(
  ({ className, variant = 'default', size = 'default', disabled, loading, children, ...props }, ref) => {
    return (
      <button
        className={clsx(
          'inline-flex items-center justify-center gap-2 rounded-2xl font-semibold transition-all duration-200',
          'focus:outline-none focus:ring-4 focus:ring-blue-100',
          'disabled:opacity-60 disabled:cursor-not-allowed disabled:shadow-none',
          buttonVariants[variant],
          buttonSizes[size],
          className
        )}
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button, buttonVariants }
