const API_BASE = '';

const agentColors = {
    'chatgpt': { emoji: '🤖', class: 'agent-chatgpt' },
    'gemini': { emoji: '✨', class: 'agent-gemini' },
    'groq': { emoji: '⚡', class: 'agent-groq' },
    'User': { emoji: '👤', class: 'agent-user' },
    'System': { emoji: '✅', class: 'agent-system' }
};

document.addEventListener('DOMContentLoaded', () => {
    loadAgentStatus();
    setupTabs();
    setupDarkMode();
});

function setupDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    const toggleIcon = darkModeToggle.querySelector('.toggle-icon');

    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        body.classList.add('dark-mode');
        toggleIcon.textContent = '☀️';
    }

    darkModeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isNowDark = body.classList.contains('dark-mode');

        toggleIcon.style.transform = 'rotate(180deg)';
        setTimeout(() => {
            toggleIcon.textContent = isNowDark ? '☀️' : '🌙';
            toggleIcon.style.transform = 'rotate(0deg)';
        }, 150);

        localStorage.setItem('darkMode', isNowDark);
    });
}

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

async function loadAgentStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();

        if (data.success) {
            displayAgentStatus(data.data.available_agents);
        }
    } catch (error) {
        console.error('Error loading agent status:', error);
        showError('Failed to load agent status. Make sure the server is running.');
    }
}

function displayAgentStatus(agents) {
    const statusDiv = document.getElementById('agentStatus');

    if (agents.length === 0) {
        statusDiv.innerHTML = '<div class="agent-badge">⚠️ No agents configured - Add API keys to config.properties</div>';
        return;
    }

    statusDiv.innerHTML = agents.map(agent => `
        <div class="agent-badge">
            ${agentColors[agent.name]?.emoji || '🤖'} ${agent.name.toUpperCase()} - ${agent.role}
        </div>
    `).join('');
}

async function runSequentialWorkflow() {
    const input = document.getElementById('sequentialInput').value.trim();

    if (!input) {
        alert('Please enter a project request');
        return;
    }

    clearConversation();
    const flowDiv = document.getElementById('conversationFlow');
    flowDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/api/workflow/sequential-stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request: input })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    handleStreamEvent(data);
                }
            }
        }
    } catch (error) {
        console.error('Error running workflow:', error);
        showError('Failed to run workflow. Check console for details.');
    }
}

function handleStreamEvent(event) {
    const flowDiv = document.getElementById('conversationFlow');

    if (event.type === 'start') {
        console.log(event.message);
        updateAnimationStatus('Workflow starting...');
        document.querySelector('.data-packet').classList.add('moving');
    } else if (event.type === 'thinking') {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = `thinking-${event.agent}`;
        thinkingDiv.className = 'agent-message thinking';
        thinkingDiv.innerHTML = `
            <div class="agent-avatar ${agentColors[event.agent]?.class || 'agent-user'}">
                ${agentColors[event.agent]?.emoji || '🤖'}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="agent-name">${event.agent}</span>
                    <span class="agent-role">${event.role}</span>
                </div>
                <div class="message-text thinking-indicator">
                    <span class="thinking-dots"></span>
                    Thinking...
                </div>
            </div>
        `;
        flowDiv.appendChild(thinkingDiv);
        flowDiv.scrollTop = flowDiv.scrollHeight;

        activateAgent(event.agent);
        updateAnimationStatus(`${event.agent} is thinking...`);
    } else if (event.type === 'message') {
        const thinkingDiv = document.getElementById(`thinking-${event.agent}`);
        if (thinkingDiv) {
            thinkingDiv.remove();
        }

        deactivateAgent(event.agent);

        addMessageToUI(event.agent, event.role, event.message);

        if (event.agent !== 'System') {
            updateAnimationStatus(`${event.agent} completed their response`);
        }
    } else if (event.type === 'error') {
        showError(`Error from ${event.agent}: ${event.error}`);
        deactivateAllAgents();
        updateAnimationStatus('Error occurred');
    } else if (event.type === 'complete') {
        console.log('Workflow complete!');
        deactivateAllAgents();
        document.querySelector('.data-packet').classList.remove('moving');
        updateAnimationStatus('✅ All done! Agents are idle.');
    }
}

function activateAgent(agentName) {
    const nodeId = `node-${agentName.toLowerCase()}`;
    const node = document.getElementById(nodeId);
    if (node) {
        node.classList.add('active');
    }
}

function deactivateAgent(agentName) {
    const nodeId = `node-${agentName.toLowerCase()}`;
    const node = document.getElementById(nodeId);
    if (node) {
        node.classList.remove('active');
    }
}

function deactivateAllAgents() {
    document.querySelectorAll('.agent-node').forEach(node => {
        node.classList.remove('active');
    });
}

function updateAnimationStatus(message) {
    const statusEl = document.getElementById('animationStatus');
    if (statusEl) {
        statusEl.textContent = message;
    }
}

function addMessageToUI(agent, role, message) {
    const flowDiv = document.getElementById('conversationFlow');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'agent-message';

    if (agent === 'User') {
        messageDiv.classList.add('user-message');
    } else if (agent === 'System') {
        messageDiv.classList.add('system-message');
    }

    const agentInfo = agentColors[agent] || agentColors['User'];
    const messageId = 'msg-' + Math.random().toString(36).substr(2, 9);

    const lineCount = message.split('\n').length;
    const shouldCollapse = lineCount > 10 || message.length > 800;

    messageDiv.innerHTML = `
        <div class="agent-avatar ${agentInfo.class}">
            ${agentInfo.emoji}
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="agent-name">${agent}</span>
                <span class="agent-role">${role || ''}</span>
            </div>
            <div id="${messageId}" class="message-text ${shouldCollapse ? 'collapsed' : ''}">${formatMessage(message)}</div>
            ${shouldCollapse ? `<button class="message-toggle" onclick="toggleMessage('${messageId}')">Show more...</button>` : ''}
        </div>
    `;

    flowDiv.appendChild(messageDiv);
    flowDiv.scrollTop = flowDiv.scrollHeight;
}

function toggleMessage(messageId) {
    const messageText = document.getElementById(messageId);
    const button = messageText.nextElementSibling;

    if (messageText.classList.contains('collapsed')) {
        messageText.classList.remove('collapsed');
        button.textContent = 'Show less';
    } else {
        messageText.classList.add('collapsed');
        button.textContent = 'Show more...';
    }
}

function formatMessage(text) {
    const escaped = escapeHtml(text);

    // First, handle properly formatted code blocks with triple backticks
    let formatted = escaped.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        const codeId = 'code-' + Math.random().toString(36).substr(2, 9);
        const lines = code.trim().split('\n').length;

        if (lines > 10 || code.length > 500) {
            return `<pre id="${codeId}" class="collapsed"><code class="language-${lang || ''}">${code}</code></pre>
                    <button class="code-toggle" onclick="toggleCode('${codeId}')">Show more...</button>`;
        }
        return `<pre><code class="language-${lang || ''}">${code}</code></pre>`;
    });

    // Auto-detect and format code blocks that aren't wrapped in backticks
    // Look for patterns like: multiple lines with code-like syntax
    formatted = formatted.replace(/\n((?:(?:[ \t]*(?:function|class|def|import|const|let|var|if|for|while|return|public|private|protected|async|await|export|interface|type)\b[^\n]*\n)|(?:[ \t]*[{}\[\];()][^\n]*\n)|(?:[ \t]+[^\n]+\n)){3,})/g, (match, code) => {
        // Check if this is already in a code block
        if (match.includes('<pre>') || match.includes('</pre>')) {
            return match;
        }

        const codeId = 'code-' + Math.random().toString(36).substr(2, 9);
        const lines = code.trim().split('\n').length;
        const trimmedCode = code.trim();

        // Detect language based on content
        let lang = '';
        if (trimmedCode.match(/\b(function|const|let|var|=>|console\.log)\b/)) lang = 'javascript';
        else if (trimmedCode.match(/\b(def|import|class|print|if __name__)\b/)) lang = 'python';
        else if (trimmedCode.match(/\b(<html|<div|<body|<script|<style)\b/)) lang = 'html';
        else if (trimmedCode.match(/\b(public|private|protected|class|interface)\b/)) lang = 'java';

        if (lines > 10 || trimmedCode.length > 500) {
            return `\n<pre id="${codeId}" class="collapsed"><code class="language-${lang}">${trimmedCode}</code></pre>
                    <button class="code-toggle" onclick="toggleCode('${codeId}')">Show more...</button>`;
        }
        return `\n<pre><code class="language-${lang}">${trimmedCode}</code></pre>`;
    });

    return formatted;
}

function toggleCode(codeId) {
    const codeBlock = document.getElementById(codeId);
    const button = codeBlock.nextElementSibling;

    if (codeBlock.classList.contains('collapsed')) {
        codeBlock.classList.remove('collapsed');
        button.textContent = 'Show less';
    } else {
        codeBlock.classList.add('collapsed');
        button.textContent = 'Show more...';
    }
}

async function runDiscussion() {
    const topic = document.getElementById('discussionTopic').value.trim();
    const rounds = parseInt(document.getElementById('discussionRounds').value);

    if (!topic) {
        alert('Please enter a discussion topic');
        return;
    }

    clearConversation();
    const flowDiv = document.getElementById('conversationFlow');
    flowDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/api/workflow/discussion-stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, rounds })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    handleStreamEvent(data);
                }
            }
        }
    } catch (error) {
        console.error('Error running discussion:', error);
        showError('Failed to run discussion. Check console for details.');
    }
}

function displayConversation(conversation) {
    const flowDiv = document.getElementById('conversationFlow');
    flowDiv.innerHTML = '';

    conversation.forEach((msg, index) => {
        const agentInfo = agentColors[msg.agent] || agentColors['User'];

        const messageDiv = document.createElement('div');
        messageDiv.className = 'agent-message';
        messageDiv.style.animationDelay = `${index * 0.1}s`;

        messageDiv.innerHTML = `
            <div class="agent-avatar ${agentInfo.class}">
                ${agentInfo.emoji}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="agent-name">${msg.agent}</span>
                    <span class="agent-role">${msg.role || ''}</span>
                </div>
                <div class="message-text">${escapeHtml(msg.message)}</div>
            </div>
        `;

        flowDiv.appendChild(messageDiv);
    });

    flowDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function clearConversation() {
    const flowDiv = document.getElementById('conversationFlow');
    flowDiv.innerHTML = '<div class="empty-state"><p>Conversation cleared. Starting fresh...</p></div>';
}

async function resetConversation() {
    if (!confirm('Are you sure you want to reset the conversation?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/reset`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            clearConversation();
            document.getElementById('conversationFlow').innerHTML = `
                <div class="empty-state">
                    <p>👆 Start a workflow or discussion to see agents collaborate</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
        showError('Failed to reset conversation');
    }
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    const flowDiv = document.getElementById('conversationFlow');
    flowDiv.innerHTML = `
        <div class="empty-state" style="color: #e74c3c;">
            <p>❌ Error: ${escapeHtml(message)}</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        if (e.target.id === 'discussionTopic') {
            runDiscussion();
        }
    }
});
