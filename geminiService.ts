
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { AppIdea, AppPlan, ChatMessage, ProjectFile, RefactorPlan, IdeationResult } from '../types.ts';
import { personas } from './personas.ts';

// This check is crucial for a web-based app where env vars aren't guaranteed.
const API_KEY = (window as any).GEMINI_API_KEY || process.env.API_KEY;

let ai: GoogleGenAI | null = null;
if (API_KEY) {
    ai = new GoogleGenAI({ apiKey: API_KEY });
} else {
    console.warn("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.");
}

export const isApiConfigured = () => !!ai;

// Exported helper to be used across the app
export const parseJsonResponse = <T,>(text: string): T | null => {
    let jsonStr = text.trim();
    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = jsonStr.match(fenceRegex);
    if (match && match[2]) {
        jsonStr = match[2].trim();
    }
    try {
        return JSON.parse(jsonStr) as T;
    } catch (e) {
        console.error("Failed to parse JSON response:", e, "Original text:", text);
        return null;
    }
};

const extractCode = (text: string): string => {
    let code = text.trim();
    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = code.match(fenceRegex);
    if (match && match[2]) {
        code = match[2].trim();
    }
    return code;
}

const callAi = async (model: string, config: any) => {
    if (!ai) throw new Error("Gemini API key not configured.");
    return await ai.models.generateContent({ model, ...config });
}


export const performIdeation = async (idea: AppIdea): Promise<IdeationResult | null> => {
    const prompt = `
You are a Product Strategist and Market Research Analyst.
Your task is to analyze a user's application idea, research the competitive landscape, and propose unique features to make the app stand out.

**App Idea:** ${idea.prompt}

**Instructions:**
1.  Use the Google Search tool to find 2-3 main competitors for this application idea.
2.  For each competitor, briefly describe their product and list 1-2 key strengths and weaknesses.
3.  Based on your analysis, generate a list of 3-5 unique "differentiators" or "featureSuggestions" that would make the user's app more competitive or innovative.
4.  Respond with a single JSON object containing:
    - \`competitors\`: An array of objects, each with \`name\`, \`description\`, \`strengths\`, and \`weaknesses\`.
    - \`differentiators\`: An array of strings describing unique selling points.
    - \`featureSuggestions\`: An array of strings for specific new features.
`;
    try {
        const response = await callAi("gemini-2.5-flash-preview-04-17", {
            contents: prompt,
            config: {
                ...personas['Market Analyst'],
                tools: [{googleSearch: {}}],
                responseMimeType: "application/json",
            },
        });
        const parsed = parseJsonResponse<IdeationResult>(response.text);
        return (parsed && parsed.competitors && parsed.featureSuggestions) ? parsed : null;
    } catch(e) {
        console.error("Ideation phase failed:", e);
        return null;
    }
};

export const refinePromptWithIdeation = async (originalPrompt: string, selectedFeatures: string[]): Promise<string | null> => {
    if (selectedFeatures.length === 0) {
        return originalPrompt;
    }

    const prompt = `
You are a Senior Product Manager. Your task is to refine a user's initial application idea by seamlessly integrating a list of selected features.

**Original Idea:**
"${originalPrompt}"

**Selected Differentiating Features to Integrate:**
- ${selectedFeatures.join('\n- ')}

**Instructions:**
Rewrite the "Original Idea" into a new, single, cohesive paragraph that sounds like a unified product vision. It should naturally incorporate all the "Selected Differentiating Features". Do not just list the features.

Respond with ONLY the refined paragraph.
`;

    try {
        const response = await callAi("gemini-2.5-flash-preview-04-17", {
            contents: prompt,
            config: {
                ...personas['Product Strategist'],
                temperature: 0.6,
            }
        });
        return response.text.trim();
    } catch (e) {
        console.error("Prompt refinement failed:", e);
        return originalPrompt; // Fallback to original prompt
    }
};


export const generateAppPlan = async (idea: AppIdea): Promise<AppPlan | null> => {
    const prompt = `
Based on the following application idea, create a comprehensive development plan.

**App Idea:** ${idea.prompt}
${idea.githubRepoUrl ? `\n**Note:** This is an existing project. The file structure should reflect the ingested repository at ${idea.githubRepoUrl}.` : ''}

**Instructions:**
Generate a JSON object that includes:
1.  **projectName**: A catchy, suitable name for the project.
2.  **description**: A one-sentence description of the application.
3.  **techStack**: An object with keys 'frontend', 'backend', 'database', and 'deployment', each containing an array of recommended technology names (e.g., "React", "Node.js", "PostgreSQL", "Docker").
4.  **fileStructure**: A recursive array of objects representing the project's file and directory structure. Each object must have:
    - **path**: The full path of the file or directory (e.g., "src/components/Button.tsx").
    - **type**: Either "file" or "directory".
    - **children**: An array of file objects for directories, or an empty array for files.

**Example of fileStructure:**
"fileStructure": [
  { "path": "src", "type": "directory", "children": [
    { "path": "src/index.tsx", "type": "file", "children": [] },
    { "path": "src/components", "type": "directory", "children": [
      { "path": "src/components/Button.tsx", "type": "file", "children": [] }
    ]}
  ]},
  { "path": "package.json", "type": "file", "children": [] }
]

Respond with ONLY the JSON object.
`;

    const response: GenerateContentResponse = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...personas['Software Architect'],
            responseMimeType: "application/json",
            temperature: 0.5,
        }
    });

    return parseJsonResponse<AppPlan>(response.text);
};


export const generatePlanFromImage = async (appIdea: string, imageBase64: string): Promise<AppPlan | null> => {
     const imagePart = {
        inlineData: {
            mimeType: 'image/png',
            data: imageBase64,
        },
    };
    const textPart = {
        text: `
You are a UI/UX expert and software architect. Analyze this image of a web interface design.
Based on the design and the user's general idea, create a complete development plan.

**App Idea:** ${appIdea}

**Instructions:**
Analyze the image and generate a JSON object that includes:
1.  **projectName**: A catchy name for the project.
2.  **description**: A one-sentence description.
3.  **techStack**: A recommended tech stack (frontend, backend, database, deployment). Assume React with TailwindCSS for the frontend.
4.  **fileStructure**: A detailed file structure based on the components you see in the image. For example, if you see a header, a sidebar, and a main content area, create files like \`src/components/Header.tsx\`, \`src/components/Sidebar.tsx\`, etc.

Respond with ONLY the JSON object.
`};

    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: { parts: [textPart, imagePart] },
        config: {
            ...personas['UI/UX Expert'],
            responseMimeType: "application/json",
            temperature: 0.4,
        }
    });
     return parseJsonResponse<AppPlan>(response.text);
};


export const generateCodeForFile = async (file: ProjectFile, plan: AppPlan, knowledge: string, allFiles: ProjectFile[]): Promise<{ code: string, planModificationRequest?: any }> => {
    const fileTree = allFiles.map(f => f.path).join('\n');
    
    const contextFiles = allFiles.filter(f => f.status === 'generated' || f.status === 'modified');
    const contextCode = contextFiles.map(f => `
// File: ${f.path}
\`\`\`
${f.code}
\`\`\`
`).join('\n\n---\n\n');

    const prompt = `
Generate production-ready code for a specific file within a larger application plan.

**Project Name:** ${plan.projectName}
**Project Description:** ${plan.description}
**Tech Stack:** ${JSON.stringify(plan.techStack)}

**Relevant Knowledge from Past Successes:**
${knowledge || "No specific knowledge applies to this file."}

**Full File Structure:**
${fileTree}

---

**Code from other relevant files for context:**
${contextCode || "No other files have been generated yet."}

---

**Current File to Generate:**
Path: ${file.path}

**Instructions:**
1.  Generate the code for the specified file path: ${file.path}.
2.  The code should be based on the project's tech stack and its purpose within the file structure.
3.  Use the provided context from other files to ensure consistency, correct imports, and proper function/component usage.
4.  **Adaptive Planning**: If you determine that a new file is necessary to support the current file (e.g., a new CSS file, a utility function), respond with a JSON object containing a 'planModificationRequest' key. Otherwise, respond with raw code.
    - Example JSON for creating a new file: \`{"planModificationRequest": {"action": "createFile", "path": "src/components/Button.css", "reason": "Extracted styles for the button component."}, "code": "import './Button.css';\\n// ... rest of Button.tsx code"}\`
5.  Respond with only the raw code for the file, unless making a plan modification request. Do not include explanations, file paths, or markdown fences in the raw code response.
`;
    
    let persona = personas['Full-Stack Developer'];
    if (file.path.includes('src/components') || file.path.endsWith('.css') || file.path.endsWith('tailwind.config.js')) {
        persona = personas['Frontend Expert'];
    } else if (file.path.startsWith('src/server') || file.path.startsWith('src/api') || file.path.endsWith('controller.js')) {
        persona = personas['Backend Expert'];
    }


    const response: GenerateContentResponse = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...persona,
            temperature: 0.3,
        }
    });

    const responseText = response.text.trim();
    const parsedJson = parseJsonResponse<{ code: string, planModificationRequest?: any }>(responseText);

    if (parsedJson && parsedJson.code) {
        return parsedJson;
    }
    
    return { code: extractCode(responseText) };
};

export const chatWithOrchestrator = async (history: ChatMessage[], plan: AppPlan | null, currentFile: ProjectFile | null): Promise<string> => {
    let persona = { ...personas['Orchestrator'] };

    let systemInstruction = persona.systemInstruction;
    systemInstruction += `
- If the user asks to "change", "refactor", "add", "fix", or otherwise modify the code, assume they are referring to the currently open file. 
- When modifying code, you MUST respond with a single JSON object with two keys: "explanation" (a string describing the change) and "code" (a string containing the complete, updated code for the file).
- If you are not modifying code, respond with a plain string.

Current Project Context:
`;

    if (plan) {
        systemInstruction += `**Project Name:** ${plan.projectName}\n`;
        systemInstruction += `**Description:** ${plan.description}\n`;
        systemInstruction += `**Tech Stack:** ${JSON.stringify(plan.techStack)}\n`;
        systemInstruction += `**File Structure:**\n${plan.fileStructure.map(f => f.path).join('\n')}\n`;
    }

    if (currentFile) {
        systemInstruction += `\n**Currently Viewing File: ${currentFile.path}**\n`;
        systemInstruction += `\`\`\`\n${currentFile.code || '// This file has not been generated yet.'}\n\`\`\``;
    }
    
    const contents = history.map(msg => ({
        role: msg.role === 'system' ? 'model' : msg.role,
        parts: [{ text: msg.content }]
    }));
    
    const response: GenerateContentResponse = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: [...contents],
        config: {
            systemInstruction: systemInstruction,
            temperature: 0.7,
        }
    });

    return response.text.trim();
};

export const generateTestError = async (code: string): Promise<{ isSuccess: boolean; errorMessage?: string }> => {
    const prompt = `
You are a QA Engineer reviewing a piece of code.
With a 30% probability, find a plausible-sounding bug in the code. If you find a bug, create a fake error message for it.
If you don't find a bug (70% probability), declare it a success.

**Code:**
\`\`\`
${code}
\`\`\`

Respond with ONLY a JSON object with one or two keys:
1.  \`isSuccess\`: a boolean (\`true\` or \`false\`).
2.  \`errorMessage\`: a string with the fake error message if \`isSuccess\` is \`false\`.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...personas['QA Engineer'],
            responseMimeType: "application/json",
            temperature: 1,
        }
    });
    return parseJsonResponse<{ isSuccess: boolean; errorMessage?: string }>(response.text) ?? { isSuccess: true };
};

export const debugCode = async (failingCode: string, errorMessage: string): Promise<string> => {
    const prompt = `
The following code has failed a test with a specific error message.
Your task is to analyze the code and the error, fix the bug, and return the complete, corrected code.

**Error Message:**
\`\`\`
${errorMessage}
\`\`\`

**Failing Code:**
\`\`\`
${failingCode}
\`\`\`

Respond with ONLY the full, corrected code. Do not add any explanations or markdown fences.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...personas['Debugger'],
            temperature: 0.2,
        }
    });
    return extractCode(response.text);
};


export const checkForMissingDependencies = async (errorMessage: string): Promise<string | null> => {
     const prompt = `
You are a dependency analysis bot. You analyze error messages to see if they are caused by a missing npm package.

**Error Message:**
\`\`\`
${errorMessage}
\`\`\`

**Instructions:**
If the error message indicates a missing package (e.g., "Cannot find module 'react-router-dom'", "Module not found: Error: Can't resolve 'axios'"), respond with a JSON object containing the name of the missing package: \`{"packageName": "axios"}\`.
If the error is not a missing dependency, respond with: \`{"packageName": null}\`.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            responseMimeType: "application/json",
        }
    });
    const result = parseJsonResponse<{packageName: string | null}>(response.text);
    return result?.packageName ?? null;
}

export const addPackageDependency = async (packageJsonCode: string, packageName: string): Promise<string> => {
    const prompt = `
You are a build engineer. Add a new dependency to the provided package.json content.
Use the latest version for the new package.

**Package to add:** ${packageName}

**Current package.json:**
\`\`\`json
${packageJsonCode}
\`\`\`

Respond with ONLY the complete, updated content of the package.json file.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...personas['DevOps Engineer'],
            temperature: 0,
        }
    });
    return extractCode(response.text);
}

export const refactorCodebase = async (allFiles: ProjectFile[]): Promise<RefactorPlan | null> => {
    const contextCode = allFiles
        .filter(f => f.code)
        .map(f => `
// File: ${f.path}
\`\`\`
${f.code}
\`\`\`
`).join('\n\n---\n\n');

    const prompt = `
Analyze the full source code of the following files. Identify any repeated logic, poor patterns, or opportunities for abstraction (e.g., creating a reusable function, component, or custom hook).

**Full Codebase:**
${contextCode}

**Instructions:**
1.  If you find a good opportunity for refactoring, create a plan.
2.  Your plan must be a JSON object with three keys:
    - \`reasoning\`: A string explaining why the refactoring is needed and what it will accomplish.
    - \`newFile\`: (Optional) An object with \`path\` and \`code\` for a new utility file to be created.
    - \`filesToUpdate\`: An array of objects, each with a \`path\` and the \`newCode\` for an existing file that needs to be updated to use the new abstraction.
3. If no significant refactoring is needed, respond with \`null\`.
`;

    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: {
            ...personas['Senior Architect'],
            responseMimeType: "application/json",
            temperature: 0.4,
        }
    });

    const text = response.text.trim();
    if (text.toLowerCase() === 'null') {
        return null;
    }
    return parseJsonResponse<RefactorPlan>(text);
};


export const performSelfDirectedLearning = async (plan: AppPlan): Promise<{searchQuery: string; insight: string} | null> => {
    const prompt = `
You are an R&D engineer for an autonomous software development team. Your goal is to use your idle time to research ways to improve the current project.

**Current Project Plan:**
- **Name:** ${plan.projectName}
- **Description:** ${plan.description}
- **Tech Stack:** ${JSON.stringify(plan.techStack, null, 2)}

**Instructions:**
1.  Formulate a single, highly relevant search query to find a best practice, a security improvement, a performance optimization, or a better implementation pattern related to the project's tech stack and description.
2.  Use the provided Google Search tool to execute this query.
3.  Analyze the search results.
4.  Synthesize your findings into a single, concise, and actionable insight. This insight should be a suggestion that could be directly applied to the project.
5.  Respond with a single JSON object containing two keys: "searchQuery" (the exact query you used) and "insight" (your synthesized recommendation).

**Example of a good insight:** "For our real-time collaborative app, instead of basic REST endpoints for chat, we should use WebSockets with the 'ws' library on our Node.js backend for much lower latency and better user experience."

Do not respond with anything other than the JSON object.
`;

    try {
        const response = await callAi("gemini-2.5-flash-preview-04-17", {
            contents: prompt,
            config: {
                ...personas['Orchestrator'],
                tools: [{googleSearch: {}}],
                responseMimeType: "application/json",
            },
        });

        const parsed = parseJsonResponse<{searchQuery: string; insight: string}>(response.text);
        if (parsed && parsed.insight && parsed.searchQuery) {
            return parsed;
        }
        return null;
    } catch(e) {
        console.error("Self-directed learning failed:", e);
        return null;
    }
};

export const generateCICDFile = async (plan: AppPlan): Promise<string | null> => {
    const prompt = `
Based on the project's tech stack, generate a complete, best-practice GitHub Actions workflow file (\`ci.yml\`) for CI/CD.

**Project Tech Stack:**
- Frontend: ${plan.techStack.frontend.join(', ')}
- Backend: ${plan.techStack.backend.join(', ')}
- Database: ${plan.techStack.database}

**Requirements:**
- The workflow should trigger on push/pull_request to the main branch.
- Include jobs for:
  - Linting the code.
  - Running tests (you can assume \`npm test\`).
  - Building the application (you can assume \`npm run build\`).
- Use a Node.js environment.

Respond with ONLY the raw YAML content for the \`ci.yml\` file.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: { ...personas['DevOps Engineer'] }
    });
    return extractCode(response.text);
};


export const generateApiClient = async (openapiSpec: string): Promise<string | null> => {
    const prompt = `
You are given an OpenAPI 3.0 specification.
Your task is to generate a fully-typed TypeScript client/SDK for consuming this API.
The client should be self-contained in a single file and use the 'axios' library for making HTTP requests.

**OpenAPI Specification:**
\`\`\`yaml
${openapiSpec}
\`\`\`

Respond with ONLY the raw TypeScript code for the generated client.
`;
     const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: { ...personas['Backend Expert'] }
    });
    return extractCode(response.text);
};

export const generateMigrationFile = async (plan: AppPlan): Promise<string | null> => {
    const prompt = `
Based on the project plan, generate an SQL migration file to create the necessary tables.

**Project:** ${plan.projectName}
**Description:** ${plan.description}
**Database:** ${plan.techStack.database}

**Instructions:**
- Analyze the project description and infer the required tables and columns.
- For a collaborative whiteboard app, you might need 'users', 'whiteboards', and 'elements' tables.
- Generate the 'CREATE TABLE' SQL statements.
- Use appropriate data types for a PostgreSQL database.

Respond with ONLY the raw SQL code for the migration file.
`;
    const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: { ...personas['DB Architect'] }
    });
    return extractCode(response.text);
};

export const runSecurityAudit = async (plan: AppPlan, files: ProjectFile[]): Promise<string> => {
    const packageJson = files.find(f => f.path === 'package.json')?.code || '{}';
    const allCode = files.filter(f => f.code && f.path.endsWith('.tsx')).map(f => `// ${f.path}\n${f.code}`).join('\n\n');

    const prompt = `
Perform a brief security audit of the provided project.

**Project:** ${plan.projectName}
**Tech Stack:** ${JSON.stringify(plan.techStack)}

**package.json:**
\`\`\`json
${packageJson}
\`\`\`

**Source Code Sample:**
\`\`\`typescript
${allCode.substring(0, 4000)}...
\`\`\`

**Instructions:**
1.  Analyze the dependencies in \`package.json\` for any obvious or common vulnerabilities.
2.  Briefly scan the source code for common web vulnerabilities (e.g., use of \`dangerouslySetInnerHTML\` in React, potential XSS vectors).
3.  Provide a short, summary report of your findings. If no issues are found, state that. Format the output as plain text.

Respond with ONLY the text-based summary report.
`;
     const response = await callAi('gemini-2.5-flash-preview-04-17', {
        contents: prompt,
        config: { ...personas['Security Analyst'] }
    });
    return response.text;
};
