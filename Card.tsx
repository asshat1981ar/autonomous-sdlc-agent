
import React from 'react';

interface CardProps {
    title: string;
    children: React.ReactNode;
    className?: string;
    role?: string;
    'aria-labelledby'?: string;
    'aria-describedby'?: string;
    id?: string;
}

const Card: React.FC<CardProps> = ({ 
    title, 
    children, 
    className,
    role = 'region',
    'aria-labelledby': ariaLabelledBy,
    'aria-describedby': ariaDescribedBy,
    id
}) => {
    const titleId = id ? `${id}-title` : undefined;
    const contentId = id ? `${id}-content` : undefined;

    return (
        <div 
            className={`bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg ${className}`}
            role={role}
            aria-labelledby={ariaLabelledBy || titleId}
            aria-describedby={ariaDescribedBy || contentId}
        >
            <div className="px-6 py-4 border-b border-gray-700">
                <h3 
                    id={titleId}
                    className="text-xl font-bold text-white"
                >
                    {title}
                </h3>
            </div>
            <div 
                id={contentId}
                className="p-6"
            >
                {children}
            </div>
        </div>
    );
};

export default Card;
