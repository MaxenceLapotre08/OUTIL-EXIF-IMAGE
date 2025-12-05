'use client';

import { FileType } from 'lucide-react';

interface FormatSelectorProps {
    value: 'jpeg' | 'png' | 'webp';
    onChange: (value: 'jpeg' | 'png' | 'webp') => void;
}

const formats = [
    { value: 'jpeg' as const, label: 'JPEG', description: 'Best for photos' },
    { value: 'png' as const, label: 'PNG', description: 'Lossless quality' },
    { value: 'webp' as const, label: 'WEBP', description: 'Modern format' },
];

export function FormatSelector({ value, onChange }: FormatSelectorProps) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-foreground flex items-center gap-2">
                <FileType className="w-4 h-4 text-primary" />
                Output Format
            </label>
            <div className="grid grid-cols-3 gap-3">
                {formats.map((format) => (
                    <button
                        key={format.value}
                        onClick={() => onChange(format.value)}
                        className={`
              p-4 rounded-lg text-center transition-all cursor-pointer
              ${value === format.value
                                ? 'bg-primary text-primary-foreground shadow-lg scale-105'
                                : 'glass hover:bg-secondary/70 text-foreground hover-lift'
                            }
            `}
                    >
                        <div className="font-semibold text-sm">{format.label}</div>
                        <div className="text-xs mt-1 opacity-80">{format.description}</div>
                    </button>
                ))}
            </div>
        </div>
    );
}
