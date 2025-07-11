import React from 'react';

interface IdeationResult {
    competitors: Array<{
        name: string;
        description: string;
        strengths: string[];
        weaknesses: string[];
    }>;
    differentiators: string[];
    featureSuggestions: string[];
}

interface IdeationViewProps {
    result: IdeationResult;
    originalPrompt: string;
    onSubmit: (selectedFeatures: string[]) => void;
    isLoading: boolean;
}

const IdeationView: React.FC<IdeationViewProps> = ({ result, originalPrompt, onSubmit, isLoading }) => {
    const [selectedFeatures, setSelectedFeatures] = React.useState<string[]>([]);

    const handleFeatureToggle = (feature: string) => {
        setSelectedFeatures(prev => 
            prev.includes(feature) 
                ? prev.filter(f => f !== feature)
                : [...prev, feature]
        );
    };

    const handleSubmit = () => {
        onSubmit(selectedFeatures);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold mb-8">Ideation Analysis</h1>
                
                <div className="mb-8 p-4 bg-gray-800 rounded-lg">
                    <h2 className="text-xl font-semibold mb-2">Original Idea</h2>
                    <p className="text-gray-300">{originalPrompt}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div>
                        <h2 className="text-xl font-semibold mb-4">Competitors</h2>
                        <div className="space-y-4">
                            {result.competitors.map((competitor, index) => (
                                <div key={index} className="p-4 bg-gray-800 rounded-lg">
                                    <h3 className="font-semibold text-blue-400">{competitor.name}</h3>
                                    <p className="text-gray-300 mb-2">{competitor.description}</p>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <h4 className="text-sm font-medium text-green-400">Strengths</h4>
                                            <ul className="text-sm text-gray-300">
                                                {competitor.strengths.map((strength, i) => (
                                                    <li key={i}>• {strength}</li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-medium text-red-400">Weaknesses</h4>
                                            <ul className="text-sm text-gray-300">
                                                {competitor.weaknesses.map((weakness, i) => (
                                                    <li key={i}>• {weakness}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h2 className="text-xl font-semibold mb-4">Differentiators</h2>
                        <div className="space-y-2 mb-8">
                            {result.differentiators.map((diff, index) => (
                                <div key={index} className="p-3 bg-gray-800 rounded-lg">
                                    <p className="text-gray-300">{diff}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="mb-8">
                    <h2 className="text-xl font-semibold mb-4">Feature Suggestions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {result.featureSuggestions.map((feature, index) => (
                            <div key={index} className="flex items-center space-x-3">
                                <input
                                    type="checkbox"
                                    id={`feature-${index}`}
                                    checked={selectedFeatures.includes(feature)}
                                    onChange={() => handleFeatureToggle(feature)}
                                    className="w-5 h-5 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
                                />
                                <label htmlFor={`feature-${index}`} className="text-gray-300 cursor-pointer">
                                    {feature}
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        onClick={handleSubmit}
                        disabled={isLoading || selectedFeatures.length === 0}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                    >
                        {isLoading ? 'Processing...' : 'Continue with Selected Features'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default IdeationView;
