import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface ArchitectureDiagramViewProps {
    fileStructure: any; // Replace with a more specific type
    projectName: string;
}

const ArchitectureDiagramView: React.FC<ArchitectureDiagramViewProps> = ({ fileStructure, projectName }) => {
    const mermaidContainer = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (mermaidContainer.current && fileStructure) {
            const graphDefinition = generateMermaidGraph(fileStructure, projectName);
            mermaid.initialize({ startOnLoad: true, theme: 'dark' });
            mermaid.render('graphDiv', graphDefinition, (svgCode) => {
                if (mermaidContainer.current) {
                    mermaidContainer.current.innerHTML = svgCode;
                }
            });
        }
    }, [fileStructure, projectName]);

    const generateMermaidGraph = (files: any[], rootName: string): string => {
        let graph = 'graph TD;\n';
        graph += `    A[${rootName}] --> B(src);\n`;

        const traverse = (children: any[], parent: string) => {
            children.forEach((file, index) => {
                const id = `${parent}${index}`;
                graph += `    ${parent} --> ${id}[${file.path.split('/').pop()}];\n`;
                if (file.children) {
                    traverse(file.children, id);
                }
            });
        };

        const srcDir = files.find(f => f.path === 'src');
        if (srcDir && srcDir.children) {
            traverse(srcDir.children, 'B');
        }

        return graph;
    };

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">Architecture Diagram</h3>
            <div ref={mermaidContainer} id="mermaid-graph"></div>
        </div>
    );
};

export default ArchitectureDiagramView;

