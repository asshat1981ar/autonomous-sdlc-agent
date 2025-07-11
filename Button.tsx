
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
    variant?: 'primary' | 'secondary';
    'aria-label'?: string;
    'aria-describedby'?: string;
    loading?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
    children, 
    variant = 'primary', 
    className, 
    loading = false,
    disabled,
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedBy,
    ...props 
}) => {
    const baseClasses = "px-6 py-2.5 font-bold rounded-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed text-center relative min-h-[44px] min-w-[44px]";
    
    const variantClasses = {
        primary: "bg-cyan-600 text-white hover:bg-cyan-500 focus:ring-cyan-400 active:bg-cyan-700",
        secondary: "bg-gray-700 text-gray-200 hover:bg-gray-600 focus:ring-gray-400 active:bg-gray-800",
    };

    const isDisabled = disabled || loading;

    return (
        <button 
            className={`${baseClasses} ${variantClasses[variant]} ${className}`} 
            disabled={isDisabled}
            aria-label={ariaLabel}
            aria-describedby={ariaDescribedBy}
            aria-busy={loading}
            {...props}
        >
            {loading && (
                <span className="absolute inset-0 flex items-center justify-center">
                    <svg 
                        className="animate-spin h-5 w-5" 
                        xmlns="http://www.w3.org/2000/svg" 
                        fill="none" 
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                    >
                        <circle 
                            className="opacity-25" 
                            cx="12" 
                            cy="12" 
                            r="10" 
                            stroke="currentColor" 
                            strokeWidth="4"
                        />
                        <path 
                            className="opacity-75" 
                            fill="currentColor" 
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                    </svg>
                    <span className="sr-only">Loading...</span>
                </span>
            )}
            <span className={loading ? 'opacity-0' : 'opacity-100'}>
                {children}
            </span>
        </button>
    );
};

export default Button;
