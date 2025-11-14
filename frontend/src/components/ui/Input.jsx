import { forwardRef } from 'react'
import { clsx } from 'clsx'

const Input = forwardRef(({
  className,
  type = 'text',
  error,
  label,
  icon: Icon,
  helpText,
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={props.id}
          className="block text-sm font-semibold text-slate-700 mb-2"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
            <Icon className="w-5 h-5" aria-hidden="true" />
          </div>
        )}
        <input
          type={type}
          className={clsx(
            'flex h-12 w-full rounded-2xl border-2 bg-white text-base transition-all duration-200',
            Icon ? 'pl-12 pr-4' : 'px-4',
            'placeholder:text-slate-400',
            'focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-slate-50',
            error
              ? 'border-red-300 bg-red-50/30 focus:border-red-400 focus:ring-red-100'
              : 'border-slate-200',
            className
          )}
          ref={ref}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={helpText || error ? `${props.id}-description` : undefined}
          {...props}
        />
      </div>
      {(helpText || error) && (
        <p
          id={`${props.id}-description`}
          className={clsx(
            'mt-2 text-sm',
            error ? 'text-red-600' : 'text-slate-500'
          )}
          role={error ? 'alert' : 'status'}
        >
          {error || helpText}
        </p>
      )}
    </div>
  )
})

Input.displayName = 'Input'

export { Input }
