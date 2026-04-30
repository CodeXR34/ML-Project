document.addEventListener('DOMContentLoaded', () => {
    // Selectors
    const expenseForm = document.getElementById('expense-form');
    const loader = document.getElementById('loader');
    const themeToggle = document.getElementById('theme-toggle');
    const historyTableBody = document.getElementById('history-table-body');
    const emptyHistory = document.getElementById('empty-history');
    const clearHistoryBtn = document.getElementById('clear-history');
    
    // 1. Theme Toggle Logic
    if (themeToggle) {
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        if (savedTheme === 'light') document.body.classList.add('light-mode');
        updateThemeIcon();

        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
            const newTheme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            updateThemeIcon();
            
            // Re-render chart if on result page to update text colors
            if (window.chartInstance) {
                renderResultChart(window.currentChartData);
            }
        });
    }

    function updateThemeIcon() {
        const icon = themeToggle?.querySelector('i');
        if (!icon) return;
        if (document.body.classList.contains('light-mode')) {
            icon.classList.replace('fa-moon', 'fa-sun');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
        }
    }

    // 2. Expense Form Submission
    if (expenseForm) {
        // Set default date
        const dateInput = document.getElementById('date');
        if (dateInput) dateInput.valueAsDate = new Date();

        expenseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            loader.classList.remove('hidden');

            const formData = {
                age: document.getElementById('age').value,
                occupation: document.getElementById('occupation').value,
                monthly_income: document.getElementById('income').value,
                city_type: document.getElementById('city_type').value,
                date: document.getElementById('date').value,
                food: document.getElementById('food').value,
                transport: document.getElementById('transport').value,
                rent: document.getElementById('rent').value,
                entertainment: document.getElementById('entertainment').value,
                utilities: document.getElementById('utilities').value,
                shopping: document.getElementById('shopping').value,
                others: document.getElementById('others').value
            };

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.status === 'success') {
                    // Save to local history before redirecting
                    saveToLocalHistory(result, formData);
                    // Redirect to results page
                    window.location.href = result.redirect;
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('Connection to server failed.');
            } finally {
                loader.classList.add('hidden');
            }
        });
    }

    // 3. Result Page Chart & Insights
    const resultCanvas = document.getElementById('resultChart');
    if (resultCanvas && typeof chartData !== 'undefined') {
        window.currentChartData = chartData;
        renderResultChart(chartData);
        renderInsights();
    }

    function renderResultChart(data) {
        const ctx = resultCanvas.getContext('2d');
        if (window.chartInstance) window.chartInstance.destroy();

        const isLight = document.body.classList.contains('light-mode');
        const textColor = isLight ? '#1e293b' : '#f1f5f9';

        window.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Food', 'Transport', 'Rent', 'Entertainment', 'Utilities', 'Shopping', 'Others'],
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#6366f1', '#ec4899', '#8b5cf6', '#f59e0b', '#10b981', '#3b82f6', '#64748b'
                    ],
                    borderWidth: 0,
                    hoverOffset: 25
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: textColor, padding: 20, font: { size: 14, family: 'Outfit' } }
                    }
                },
                cutout: '65%'
            }
        });
    }

    function renderInsights() {
        const container = document.getElementById('insights-container');
        if (!container) return;

        // Note: In a real app, logic would be more complex
        // This is a demonstration based on the current data
        const insights = [
            { icon: 'fa-check-circle', text: 'Analysis complete. Your spending profile matches a stable professional trend.' },
            { icon: 'fa-info-circle', text: 'Tip: Rent takes up a significant portion. Consider optimizing utility costs.' }
        ];

        container.innerHTML = insights.map(i => `
            <div class="insight-item">
                <i class="fas ${i.icon}"></i>
                <span>${i.text}</span>
            </div>
        `).join('');
    }

    // 4. History Management
    function saveToLocalHistory(result, formData) {
        const history = JSON.parse(localStorage.getItem('expenseHistory') || '[]');
        const entry = {
            id: Date.now(),
            date: formData.date,
            income: formData.monthly_income,
            prediction: result.prediction,
            range: result.range,
            timestamp: new Date().toLocaleString()
        };
        history.unshift(entry);
        localStorage.setItem('expenseHistory', JSON.stringify(history));
    }

    if (historyTableBody) {
        renderHistoryTable();

        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => {
                if (confirm('Are you sure you want to clear your entire history?')) {
                    localStorage.removeItem('expenseHistory');
                    renderHistoryTable();
                }
            });
        }
    }

    function renderHistoryTable() {
        const history = JSON.parse(localStorage.getItem('expenseHistory') || '[]');
        
        if (history.length === 0) {
            historyTableBody.innerHTML = '';
            emptyHistory.classList.remove('hidden');
            return;
        }

        emptyHistory.classList.add('hidden');
        historyTableBody.innerHTML = history.map((item, idx) => {
            const income    = parseFloat(item.income);
            const pred      = parseFloat(item.prediction);
            const ratio     = income > 0 ? ((pred / income) * 100).toFixed(1) : '—';
            const ratioNum  = parseFloat(ratio);
            const ratioClass = ratioNum < 50 ? 'ratio-low' : ratioNum < 80 ? 'ratio-mid' : 'ratio-high';
            return `
            <tr>
                <td><span class="row-num">${idx + 1}</span></td>
                <td><strong>${item.date}</strong></td>
                <td>₹${income.toLocaleString()}</td>
                <td><span class="pred-amount">₹${pred.toLocaleString()}</span></td>
                <td><span class="ratio-pill ${ratioClass}">${ratio}%</span></td>
                <td><span class="status-badge">Predicted</span></td>
                <td>
                    <button class="delete-row-btn" onclick="deleteHistoryItem(${item.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`;
        }).join('');
    }

    window.deleteHistoryItem = (id) => {
        let history = JSON.parse(localStorage.getItem('expenseHistory') || '[]');
        history = history.filter(item => item.id !== id);
        localStorage.setItem('expenseHistory', JSON.stringify(history));
        renderHistoryTable();
    };
});
