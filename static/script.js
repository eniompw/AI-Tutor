// Wait for the DOM to be fully loaded before executing the script
document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    // DOM element references
    const elements = {
        answerInput: document.getElementById('answer'),
        submitButton: document.getElementById('submit'),
        groqOutput: document.getElementById('groq'),
        geminiOutput: document.getElementById('gemini'),
        progressBarFill: document.getElementById('progressBarFill'),
        previousButton: document.getElementById('previous'),
        nextButton: document.getElementById('next'),
        summaryHeading: document.getElementById('summary-heading'),
        detailHeading: document.getElementById('detail-heading'),
        buttonOverlay: document.querySelector('.button-overlay'),
        tryAgainButton: document.getElementById('tryAgain'),
        currentSubjectElement: document.getElementById('currentSubject')
    };

    // Progress bar animation variables
    let currentProgress = 0;
    let targetProgress = 0;
    let animationInterval;
    let waitingForGemini = false;

    // Initialize the app
    setFocus();
    loadSavedSubject();
    setupEventListeners();

    // Helper functions
    function setFocus() {
        elements.answerInput.focus();
    }

    function loadSavedSubject() {
        const savedSubject = localStorage.getItem('currentSubject') || 'computing';
        changeSubject(savedSubject, false);
    }

    function setupEventListeners() {
        elements.submitButton.addEventListener('click', fetchFeedback);
        elements.previousButton.addEventListener('click', () => navigate('previous'));
        elements.nextButton.addEventListener('click', () => navigate('next'));
        elements.tryAgainButton.addEventListener('click', tryAgain);
        document.addEventListener('keydown', handleKeyPress);
    }

    function handleKeyPress(event) {
        if (event.ctrlKey && event.key === 'Enter') fetchFeedback();
    }

    // Progress bar functions
    function updateProgressBar(progress) {
        elements.progressBarFill.style.width = `${progress}%`;
        elements.progressBarFill.textContent = `${Math.round(progress)}%`;
        elements.progressBarFill.classList.toggle('loading', progress > 0 && progress < 100);
    }

    function animateProgress() {
        if (currentProgress < targetProgress) {
            const increment = calculateIncrement();
            currentProgress = Math.min(currentProgress + increment, targetProgress);
            const easedProgress = easeOutCubic(currentProgress / 100) * 100;
            updateProgressBar(easedProgress);

            if (currentProgress >= targetProgress) {
                clearInterval(animationInterval);
                if (targetProgress === 100) updateProgressBar(100);
            }
        }
    }

    function calculateIncrement() {
        if (waitingForGemini && currentProgress >= 90) {
            return 0.1 * (1 - (currentProgress - 90) / 10);
        } else if (currentProgress >= 40 && currentProgress < 90) {
            return 0.5;
        } else {
            return 0.3;
        }
    }

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function setProgress(progress) {
        targetProgress = progress;
        clearInterval(animationInterval);
        animationInterval = setInterval(animateProgress, 50);
    }

    // UI update functions
    function markdownToHtmlBold(text) {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    function showNavigationButtons() {
        elements.buttonOverlay.classList.add('show-buttons');
        elements.tryAgainButton.style.display = 'inline-block';
        setTimeout(() => elements.tryAgainButton.classList.add('show-buttons'), 50);
    }

    function scrollToElement(element, delay = 0) {
        return new Promise(resolve => {
            setTimeout(() => {
                element.scrollIntoView({ behavior: 'smooth' });
                resolve();
            }, delay);
        });
    }

    // Main functionalities
    async function fetchFeedback() {
        const answer = encodeURIComponent(elements.answerInput.value);
        resetUI();

        try {
            await fetchGroqResponse(answer);
            await fetchGeminiResponse(answer);
        } catch (error) {
            console.error('Error fetching feedback:', error);
            setProgress(0);
        } finally {
            showNavigationButtons();
        }
    }

    async function fetchGroqResponse(answer) {
        setProgress(20);
        const response = await fetch(`/ai_response/groq?answer=${answer}`).then(res => res.text());
        setProgress(40);
        elements.groqOutput.textContent = response;
        await scrollToElement(elements.summaryHeading);
    }

    async function fetchGeminiResponse(answer) {
        setProgress(80);
        waitingForGemini = true;
        setProgress(95);
        const response = await fetch(`/ai_response/gemini?answer=${answer}`).then(res => res.text());
        waitingForGemini = false;
        setProgress(100);
        elements.geminiOutput.innerHTML = markdownToHtmlBold(response);
        await scrollToElement(elements.detailHeading);
    }

    function resetUI() {
        currentProgress = 0;
        waitingForGemini = false;
        setProgress(0);
        elements.buttonOverlay.classList.remove('show-buttons');
        elements.tryAgainButton.classList.remove('show-buttons');
        elements.tryAgainButton.style.display = 'none';
    }

    function navigate(direction) {
        fetch(`/${direction}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateQuestion(data.question);
                    resetUI();
                } else {
                    console.error(data.message);
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function updateQuestion(question) {
        document.getElementById('question').innerHTML = question;
        elements.answerInput.value = '';
        elements.groqOutput.textContent = '';
        elements.geminiOutput.textContent = '';
        setFocus();
    }

    function tryAgain() {
        elements.groqOutput.textContent = '';
        elements.geminiOutput.textContent = '';
        elements.answerInput.value = '';
        resetUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        setTimeout(setFocus, 500);
    }
}

// Burger menu functions
function toggleMenu() {
    const burgerMenu = document.querySelector('.burger-menu');
    const menu = document.getElementById("subjectMenu");
    burgerMenu.classList.toggle("change");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function changeSubject(subject, reload = true) {
    if (reload) {
        fetch(`/${subject}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateSubjectUI(data.subject);
                    window.location.reload();
                } else {
                    console.error('Failed to change subject on server');
                    updateSubjectUI(data.subject);  // Update UI with the current subject from server
                }
            })
            .catch(error => {
                console.error('Error:', error);
                updateSubjectUI(subject);  // Fallback to local update on error
            });
    } else {
        updateSubjectUI(subject);
    }
}

function updateSubjectUI(subject) {
    const currentSubjectElement = document.getElementById('currentSubject');
    currentSubjectElement.textContent = `Current Subject: ${subject.charAt(0).toUpperCase() + subject.slice(1)}`;
    
    document.querySelectorAll('.menu-content button').forEach(button => {
        button.classList.toggle('active', button.id === subject);
    });
    
    localStorage.setItem('currentSubject', subject);
    console.log(`Changed subject to: ${subject}`);
    
    document.getElementById("subjectMenu").style.display = "none";
    document.querySelector(".burger-menu").classList.remove("change");
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById("subjectMenu");
    const burgerMenu = document.querySelector('.burger-menu');
    if (!menu.contains(event.target) && !burgerMenu.contains(event.target)) {
        menu.style.display = 'none';
        burgerMenu.classList.remove("change");
    }
});