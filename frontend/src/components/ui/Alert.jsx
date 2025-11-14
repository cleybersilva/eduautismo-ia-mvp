import { forwardRef } from 'react'
import { clsx } from 'clsx'
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react'

const alertVariants = {
  default: 'bg-gray-50 text-gray-900 border-gray-200',
  destructive: 'bg-error-50 text-error-900 border-error-200',
  success: 'bg-success-50 text-success-900 border-success-200',
  warning: 'bg-warning-50 text-warning-900 border-warning-200',
  info: 'bg-primary-50 text-primary-900 border-primary-200',
}

const alertIcons = {
  default: Info,
  destructive: XCircle,
  success: CheckCircle,
  warning: AlertCircle,
  info: Info,
}

const Alert = forwardRef(({ className, variant = 'default', children, ...props }, ref) => {
  const Icon = alertIcons[variant]

  return (
    <div
      ref={ref}
      role="alert"
      className={clsx(
        'relative w-full rounded-lg border p-4',
        alertVariants[variant],
        className
      )}
      {...props}
    >
      <div className="flex gap-3">
        {Icon && <Icon className="h-5 w-5 flex-shrink-0" />}
        <div className="flex-1">{children}</div>
      </div>
    </div>
  )
})
Alert.displayName = 'Alert'

const AlertTitle = forwardRef(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={clsx('mb-1 font-medium leading-none tracking-tight', className)}
    {...props}
  />
))
AlertTitle.displayName = 'AlertTitle'

const AlertDescription = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={clsx('text-sm [&_p]:leading-relaxed', className)} {...props} />
))
AlertDescription.displayName = 'AlertDescription'

export { Alert, AlertTitle, AlertDescription }
