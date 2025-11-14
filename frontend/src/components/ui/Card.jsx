import { forwardRef } from 'react'
import { clsx } from 'clsx'

const Card = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={clsx(
      'rounded-3xl border border-slate-200 bg-white/95 backdrop-blur-sm',
      'shadow-lg shadow-slate-200/50 text-slate-900',
      'transition-shadow duration-200',
      className
    )}
    {...props}
  />
))
Card.displayName = 'Card'

const CardHeader = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={clsx('flex flex-col space-y-2 p-8', className)}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={clsx(
      'text-2xl font-bold leading-tight tracking-tight text-slate-900',
      className
    )}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

const CardDescription = forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={clsx('text-base text-slate-600 leading-relaxed', className)}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={clsx('p-8 pt-0', className)} {...props} />
))
CardContent.displayName = 'CardContent'

const CardFooter = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={clsx('flex items-center p-8 pt-0', className)}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
