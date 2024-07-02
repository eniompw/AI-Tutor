document.addEventListener('DOMContentLoaded', () => {
    // DOM element references
    const answerInput = document.getElementById('answer');
    const submitButton = document.getElementById('submit');
    const groqOutput = document.getElementById('groq');
    const geminiOutput = document.getElementById('gemini');
    const progressBarFill = document.getElementById('progressBarFill');
    const previousButton = document.getElementById('previous');
    const nextButton = document.getElementById('next');
    const summaryHeading = document.getElementById('summary-heading');
    const detailHeading = document.getElementById('detail-heading');
    const buttonOverlay = document.querySelector('.button-overlay');
    const tryAgainButton = document.getElementById('tryAgain');
    const currentSubjectElement = document.getElementById('currentSubject');

    // Variables for progress bar animation
    let currentProgress = 0;
    let targetProgress = 0;
    let animationInterval;
    let waitingForGemini = false;

    // Set focus to answer input on page load
    answerInput.focus();

    // Load saved subject from localStorage
    const savedSubject = localStorage.getItem('currentSubject') || 'computing';
    changeSubject(savedSubject, false);

    // Easing function for smooth progress bar animation
    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    // Update progress bar width and text
    function updateProgressBar(progress) {
        progressBarFill.style.width = `${progress}%`;
        progressBarFill.textContent = `${Math.round(progress)}%`;
        if (progress > 0 && progress < 100) {
            progressBarFill.classList.add('loading');
        } else {
            progressBarFill.classList.remove('loading');
        }
    }

    // Animate progress bar
    function animateProgress() {
        if (currentProgress < targetProgress) {
            let increment;
            
            // Adjust increment based on progress and waiting state
            if (waitingForGemini && currentProgress >= 90) {
                increment = 0.1 * (1 - (currentProgress - 90) / 10);
            } else if (currentProgress >= 40 && currentProgress < 90) {
                increment = 0.5;
            } else {
                increment = 0.3;
            }
            
            increment = Math.min(increment, targetProgress - currentProgress);
            currentProgress += increment;
            
            const easedProgress = easeOutCubic(currentProgress / 100) * 100;
            updateProgressBar(easedProgress);

            if (currentProgress >= targetProgress) {
                clearInterval(animationInterval);
                if (targetProgress === 100) {
                    updateProgressBar(100);
                }
            }
        }
    }

    // Set target progress and start animation
    function setProgress(progress) {
        targetProgress = progress;
        clearInterval(animationInterval);
        animationInterval = setInterval(animateProgress, 50);
    }

    // Convert markdown bold syntax to HTML
    function markdownToHtmlBold(text) {
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    // Show navigation buttons
    function showNavigationButtons() {
        buttonOverlay.classList.add('show-buttons');
        tryAgainButton.style.display = 'inline-block';
        setTimeout(() => {
            tryAgainButton.classList.add('show-buttons');
        }, 50);
    }

    // Scroll to element with optional delay
    function scrollToElement(element, delay = 0) {
        return new Promise((resolve) => {
            setTimeout(() => {
                element.scrollIntoView({ behavior: 'smooth' });
                resolve();
            }, delay);
        });
    }

    // Fetch feedback from AI models
    async function fetchFeedback() {
        const answer = encodeURIComponent(answerInput.value);

        // Reset progress and hide buttons
        currentProgress = 0;
        waitingForGemini = false;
        setProgress(0);
        buttonOverlay.classList.remove('show-buttons');
        tryAgainButton.classList.remove('show-buttons');
        tryAgainButton.style.display = 'none';

        try {
            // Fetch Groq response
            setProgress(20);
            const groqResponse = await fetch(`/ai_response/groq?answer=${answer}`).then(res => res.text());
            setProgress(40);
            groqOutput.textContent = groqResponse;
            await scrollToElement(summaryHeading);

            // Fetch Gemini response
            setProgress(80);
            waitingForGemini = true;
            setProgress(95);
            const geminiResponse = await fetch(`/ai_response/gemini?answer=${answer}`).then(res => res.text());
            waitingForGemini = false;
            setProgress(100);
            geminiOutput.innerHTML = markdownToHtmlBold(geminiResponse);
            await scrollToElement(detailHeading);
        } catch (error) {
            console.error('Error fetching feedback:', error);
            setProgress(0);
        } finally {
            showNavigationButtons();
        }
    }

    // Navigate to previous or next question
    function navigate(direction) {
        fetch(`/${direction}`).then(() => window.location.reload());
    }

    // Reset the page for a new attempt
    function tryAgain() {
        groqOutput.textContent = '';
        geminiOutput.textContent = '';
        answerInput.value = '';
        currentProgress = 0;
        setProgress(0);
        buttonOverlay.classList.remove('show-buttons');
        tryAgainButton.classList.remove('show-buttons');
        tryAgainButton.style.display = 'none';
        window.scrollTo({top: 0, behavior: 'smooth'});
        setTimeout(() => {
            answerInput.focus();
        }, 500);
    }

    // Event listeners
    submitButton.addEventListener('click', fetchFeedback);
    previousButton.addEventListener('click', () => navigate('previous'));
    nextButton.addEventListener('click', () => navigate('next'));
    tryAgainButton.addEventListener('click', tryAgain);
    
    // Submit on Ctrl + Enter
    document.addEventListener('keydown', event => {
        if (event.ctrlKey && event.key === 'Enter') fetchFeedback();
    });
});

// Burger menu functions
function toggleMenu() {
    const burgerMenu = document.querySelector('.burger-menu');
    const menu = document.getElementById("subjectMenu");
    burgerMenu.classList.toggle("change");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function changeSubject(subject, reload = true) {
    const currentSubjectElement = document.getElementById('currentSubject');
    currentSubjectElement.textContent = `Current Subject: ${subject.charAt(0).toUpperCase() + subject.slice(1)}`;
    const buttons = document.querySelectorAll('.menu-content button');
    buttons.forEach(button => {
        button.classList.remove('active');
        if (button.id === subject) {
            button.classList.add('active');
        }
    });
    
    // Save the selected subject to localStorage
    localStorage.setItem('currentSubject', subject);

    // Here you would add the logic to actually change the subject in your app
    console.log(`Changed subject to: ${subject}`);
    if (reload) {
        fetch(`/${subject}`).then(() => window.location.reload());
    }
    
    // Close the menu after selection
    document.getElementById("subjectMenu").style.display = "none";
    document.querySelector(".burger-menu").classList.remove("change");
}