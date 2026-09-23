import type { ButtonHTMLAttributes, ReactNode } from 'react';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'ghost';
  children: ReactNode;
};

export function Button({ variant = 'primary', className = '', children, type = 'button', ...props }: ButtonProps) {
  const classes = ['as-btn', `as-btn--${variant}`, className].filter(Boolean).join(' ');
  return (
    <button type={type} className={classes} {...props}>
      {children}
    </button>
  );
}
