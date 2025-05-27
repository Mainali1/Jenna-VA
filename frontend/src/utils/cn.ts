import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Utility function to merge Tailwind CSS classes with proper conflict resolution
 * 
 * This function combines clsx for conditional class names and tailwind-merge
 * for resolving Tailwind CSS class conflicts.
 * 
 * @param inputs - Class values to merge
 * @returns Merged class string
 * 
 * @example
 * ```tsx
 * // Basic usage
 * cn('px-2 py-1', 'bg-red-500')
 * // => 'px-2 py-1 bg-red-500'
 * 
 * // Conditional classes
 * cn('px-2 py-1', {
 *   'bg-red-500': isError,
 *   'bg-green-500': isSuccess
 * })
 * 
 * // Conflict resolution (tailwind-merge)
 * cn('px-2 px-4') // => 'px-4' (px-4 overrides px-2)
 * cn('bg-red-500 bg-blue-500') // => 'bg-blue-500'
 * 
 * // Complex example
 * cn(
 *   'base-class',
 *   condition && 'conditional-class',
 *   {
 *     'active-class': isActive,
 *     'disabled-class': isDisabled
 *   },
 *   className // from props
 * )
 * ```
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/**
 * Variant of cn that focuses on component variants
 * Useful for creating component variants with base classes
 * 
 * @param base - Base classes that are always applied
 * @param variants - Variant classes based on props
 * @param className - Additional classes from props
 * @returns Merged class string
 * 
 * @example
 * ```tsx
 * const buttonVariants = {
 *   variant: {
 *     primary: 'bg-blue-500 text-white',
 *     secondary: 'bg-gray-500 text-white',
 *     ghost: 'bg-transparent text-gray-900'
 *   },
 *   size: {
 *     sm: 'px-2 py-1 text-sm',
 *     md: 'px-4 py-2 text-base',
 *     lg: 'px-6 py-3 text-lg'
 *   }
 * }
 * 
 * cva(
 *   'inline-flex items-center justify-center rounded-md font-medium transition-colors',
 *   buttonVariants.variant.primary,
 *   buttonVariants.size.md,
 *   className
 * )
 * ```
 */
export function cva(
  base: string,
  ...variants: (string | undefined | null | false)[]
): string {
  return cn(base, ...variants.filter(Boolean))
}

/**
 * Creates a class name builder function for consistent component styling
 * 
 * @param baseClasses - Base classes for the component
 * @returns Function that merges base classes with additional classes
 * 
 * @example
 * ```tsx
 * const cardClasses = createClassBuilder(
 *   'rounded-lg border border-gray-200 bg-white p-4 shadow-sm'
 * )
 * 
 * // Usage in component
 * <div className={cardClasses('hover:shadow-md', className)} />
 * ```
 */
export function createClassBuilder(baseClasses: string) {
  return (...additionalClasses: ClassValue[]) => {
    return cn(baseClasses, ...additionalClasses)
  }
}

/**
 * Utility for creating responsive class names
 * 
 * @param classes - Object with breakpoint keys and class values
 * @returns Merged responsive class string
 * 
 * @example
 * ```tsx
 * responsive({
 *   base: 'text-sm',
 *   sm: 'text-base',
 *   md: 'text-lg',
 *   lg: 'text-xl',
 *   xl: 'text-2xl'
 * })
 * // => 'text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl'
 * ```
 */
export function responsive(classes: {
  base?: string
  sm?: string
  md?: string
  lg?: string
  xl?: string
  '2xl'?: string
}): string {
  const { base, sm, md, lg, xl, '2xl': xl2 } = classes
  
  return cn(
    base,
    sm && `sm:${sm}`,
    md && `md:${md}`,
    lg && `lg:${lg}`,
    xl && `xl:${xl}`,
    xl2 && `2xl:${xl2}`
  )
}

/**
 * Utility for creating state-based class names
 * 
 * @param states - Object with state keys and class values
 * @returns Merged state class string
 * 
 * @example
 * ```tsx
 * states({
 *   hover: 'hover:bg-gray-100',
 *   focus: 'focus:ring-2 focus:ring-blue-500',
 *   active: 'active:bg-gray-200',
 *   disabled: 'disabled:opacity-50 disabled:cursor-not-allowed'
 * })
 * ```
 */
export function states(states: {
  hover?: string
  focus?: string
  active?: string
  disabled?: string
  visited?: string
  checked?: string
  selected?: string
}): string {
  return cn(
    states.hover && `hover:${states.hover}`,
    states.focus && `focus:${states.focus}`,
    states.active && `active:${states.active}`,
    states.disabled && `disabled:${states.disabled}`,
    states.visited && `visited:${states.visited}`,
    states.checked && `checked:${states.checked}`,
    states.selected && `selected:${states.selected}`
  )
}

/**
 * Utility for creating dark mode class names
 * 
 * @param lightClasses - Classes for light mode
 * @param darkClasses - Classes for dark mode
 * @returns Merged class string with dark mode variants
 * 
 * @example
 * ```tsx
 * darkMode('bg-white text-gray-900', 'bg-gray-900 text-white')
 * // => 'bg-white text-gray-900 dark:bg-gray-900 dark:text-white'
 * ```
 */
export function darkMode(lightClasses: string, darkClasses: string): string {
  const darkClassList = darkClasses.split(' ').map(cls => `dark:${cls}`).join(' ')
  return cn(lightClasses, darkClassList)
}

/**
 * Utility for creating animation class names with proper timing
 * 
 * @param animation - Animation name
 * @param duration - Animation duration
 * @param timing - Animation timing function
 * @param delay - Animation delay
 * @returns Animation class string
 * 
 * @example
 * ```tsx
 * animation('fade-in', '300ms', 'ease-out', '100ms')
 * // => 'animate-fade-in duration-300 ease-out delay-100'
 * ```
 */
export function animation(
  animation: string,
  duration?: string,
  timing?: 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out',
  delay?: string
): string {
  const durationClass = duration ? `duration-${duration.replace('ms', '')}` : ''
  const timingClass = timing ? `ease-${timing}` : ''
  const delayClass = delay ? `delay-${delay.replace('ms', '')}` : ''
  
  return cn(`animate-${animation}`, durationClass, timingClass, delayClass)
}

/**
 * Utility for creating grid layout class names
 * 
 * @param cols - Number of columns or responsive column object
 * @param gap - Gap size
 * @param rows - Number of rows (optional)
 * @returns Grid class string
 * 
 * @example
 * ```tsx
 * grid(3, '4', 2)
 * // => 'grid grid-cols-3 grid-rows-2 gap-4'
 * 
 * grid({ base: 1, md: 2, lg: 3 }, '4')
 * // => 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
 * ```
 */
export function grid(
  cols: number | { base?: number; sm?: number; md?: number; lg?: number; xl?: number },
  gap?: string,
  rows?: number
): string {
  let colClasses: string
  
  if (typeof cols === 'number') {
    colClasses = `grid-cols-${cols}`
  } else {
    colClasses = cn(
      cols.base && `grid-cols-${cols.base}`,
      cols.sm && `sm:grid-cols-${cols.sm}`,
      cols.md && `md:grid-cols-${cols.md}`,
      cols.lg && `lg:grid-cols-${cols.lg}`,
      cols.xl && `xl:grid-cols-${cols.xl}`
    )
  }
  
  return cn(
    'grid',
    colClasses,
    rows && `grid-rows-${rows}`,
    gap && `gap-${gap}`
  )
}

/**
 * Utility for creating flex layout class names
 * 
 * @param direction - Flex direction
 * @param justify - Justify content
 * @param align - Align items
 * @param wrap - Flex wrap
 * @param gap - Gap size
 * @returns Flex class string
 * 
 * @example
 * ```tsx
 * flex('row', 'center', 'center', 'wrap', '4')
 * // => 'flex flex-row justify-center items-center flex-wrap gap-4'
 * ```
 */
export function flex(
  direction?: 'row' | 'col' | 'row-reverse' | 'col-reverse',
  justify?: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly',
  align?: 'start' | 'end' | 'center' | 'baseline' | 'stretch',
  wrap?: 'wrap' | 'nowrap' | 'wrap-reverse',
  gap?: string
): string {
  return cn(
    'flex',
    direction && `flex-${direction}`,
    justify && `justify-${justify}`,
    align && `items-${align}`,
    wrap && `flex-${wrap}`,
    gap && `gap-${gap}`
  )
}

export default cn