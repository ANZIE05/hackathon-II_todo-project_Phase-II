import React from 'react';
import Button from './Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  showAction?: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionText = 'Get Started',
  onAction,
  showAction = false
}) => {
  return (
    <div className="text-center py-12">
      <svg
        className="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          vectorEffect="non-scaling-stroke"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
      </svg>
      <h3 className="mt-2 text-xl font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-gray-500">{description}</p>
      {showAction && onAction && (
        <div className="mt-6">
          <Button onClick={onAction} variant="primary">
            {actionText}
          </Button>
        </div>
      )}
    </div>
  );
};

export default EmptyState;