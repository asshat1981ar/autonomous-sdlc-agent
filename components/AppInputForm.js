import React from 'react';
const AppInputForm = ({ onSubmit, isLoading, error }) => {
    const [prompt, setPrompt] = React.useState('');
    const [githubRepoUrl, setGithubRepoUrl] = React.useState('');
    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ prompt, githubRepoUrl: githubRepoUrl || undefined });
    };
    return (React.createElement("div", { className: "min-h-screen bg-gray-900 text-white flex items-center justify-center p-8" },
        React.createElement("div", { className: "max-w-md w-full" },
            React.createElement("h1", { className: "text-3xl font-bold mb-8 text-center" }, "Autonomous SDLC Agent"),
            React.createElement("form", { onSubmit: handleSubmit, className: "space-y-4" },
                React.createElement("div", null,
                    React.createElement("label", { htmlFor: "prompt", className: "block text-sm font-medium mb-2" }, "Project Idea"),
                    React.createElement("textarea", { id: "prompt", value: prompt, onChange: (e) => setPrompt(e.target.value), rows: 4, className: "w-full p-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", placeholder: "Describe your project idea...", required: true })),
                React.createElement("div", null,
                    React.createElement("label", { htmlFor: "githubUrl", className: "block text-sm font-medium mb-2" }, "GitHub Repository URL (optional)"),
                    React.createElement("input", { id: "githubUrl", type: "url", value: githubRepoUrl, onChange: (e) => setGithubRepoUrl(e.target.value), className: "w-full p-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent", placeholder: "https://github.com/username/repo" })),
                React.createElement("button", { type: "submit", disabled: isLoading, className: "w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-3 px-4 rounded-lg transition-colors" }, isLoading ? 'Processing...' : 'Start Project')),
            error && (React.createElement("div", { className: "mt-4 p-3 bg-red-900 border border-red-700 text-red-200 rounded-lg" }, error)))));
};
export default AppInputForm;
