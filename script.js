// Dark TV Series Interactive Event Visualization
// Front Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dark TV Series Visualization - Front Page Loaded');
    
    // Initialize background animations
    initializeBackgroundEffects();
    initializeVizControls();
    
    // Initialize zoom functionality after a delay to ensure iframe is ready
    setTimeout(() => {
        initializeZoom();
    }, 1500);
    
    // Add smooth scrolling for better UX
    addSmoothScrolling();
    
    // Performance optimization for animations
    optimizeAnimations();
    
    // Apply dark theme enhancements
    applyDarkThemeToSliders();
    enhancePageTransitions();
    enhanceIframeInteraction();
    
    // Add header blackening effect on scroll
    addHeaderBlackeningEffect();
});

function initializeBackgroundEffects() {
    const timeMachineEffect = document.querySelector('.time-machine-effect');
    const godParticleEffect = document.querySelector('.god-particle-effect');
    
    if (!timeMachineEffect || !godParticleEffect) {
        console.warn('Background effect elements not found');
        return;
    }
    
    // Ensure animations start correctly
    timeMachineEffect.style.animationDelay = '0s';
    godParticleEffect.style.animationDelay = '0s';
    
    // Add additional sparks dynamically for enhanced effect
    addDynamicSparks();
}

function addDynamicSparks() {
    const copperDevice = document.querySelector('.copper-device');
    if (!copperDevice) return;
    
    // Add more amber sparks dynamically for enhanced steampunk effect
    for (let i = 6; i <= 8; i++) {
        const spark = document.createElement('div');
        spark.className = `amber-spark spark-${i}`;
        
        // Position sparks around the device perimeter
        const angle = (Math.random() * 360) * (Math.PI / 180);
        const radius = 90; // Distance from center
        const centerX = 100;
        const centerY = 100;
        
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        spark.style.top = y + 'px';
        spark.style.left = x + 'px';
        spark.style.animationDelay = Math.random() * 2 + 's';
        spark.style.animationDuration = (Math.random() * 0.8 + 1.2) + 's';
        spark.style.transform = `rotate(${angle * (180 / Math.PI)}deg)`;
        
        copperDevice.appendChild(spark);
    }
}

function initializeVizControls() {
    const vizContainer = document.querySelector('.visualization-container');
    const iframeWrapper = vizContainer.querySelector('.iframe-scroll-wrapper');
    const iframe = iframeWrapper ? iframeWrapper.querySelector('iframe') : null;
    
    if (!vizContainer || !iframeWrapper || !iframe) {
        console.warn('Required elements not found for viz controls');
        return;
    }

    // Mobile detection function
    const isMobile = () => {
        return window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };

    // Create loading overlay
    const loadingOverlay = createLoadingOverlay();
    vizContainer.appendChild(loadingOverlay);

    // Setup external scrolling for the iframe
    setupExternalScrolling(iframe, iframeWrapper);

    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'viz-controls';

    const buttons = [
        { text: 'Interactive Timeline', src: 'Visualization.html', height: 700, desktopOnly: true }, 
        //{ text: 'Static Timeline (Alt)', src: '../Visualization/dark_timeline_grid(yungtversion).html', height: 725 }, 
        { text: 'Timeline Image', src: 'Visualization.png', type: 'image', height: 700 } 
    ];

    buttons.forEach(btnInfo => {
        const button = document.createElement('button');
        button.className = 'viz-btn';
        
        // Check if this is a desktop-only button on mobile
        const isDesktopOnlyOnMobile = btnInfo.desktopOnly && isMobile();
        
        if (isDesktopOnlyOnMobile) {
            button.innerHTML = `🔒 ${btnInfo.text}`;
            button.classList.add('locked');
            button.title = 'This feature is only available on desktop';
        } else {
            button.textContent = btnInfo.text;
        }

        button.addEventListener('click', () => {
            // If this is a locked button, show message and return
            if (isDesktopOnlyOnMobile) {
                showDesktopOnlyMessage();
                return;
            }
            
            // Show loading overlay
            showLoadingOverlay(loadingOverlay);
            
            // Remove active class from all buttons
            controlsContainer.querySelectorAll('.viz-btn').forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            button.classList.add('active');            // Set iframe height based on content type and update wrapper
            const currentHeight = 725; 
            iframe.style.height = currentHeight + 'px';
            iframeWrapper.style.height = currentHeight + 'px';
            
            // For wider content, we need to set the iframe to be wider than its container
            // so the scroll wrapper can provide external scrollbars
            if (btnInfo.type !== 'image') {
                // Set iframe to be wider to accommodate full content width
                iframe.style.width = '150%'; // This will trigger horizontal scrolling in the wrapper
                iframe.style.minWidth = '1400px'; // Minimum width for timeline content
            } else {
                iframe.style.width = '100%';
                iframe.style.minWidth = 'auto';
            }
            
            // Update visualization container height to accommodate iframe
            vizContainer.style.minHeight = (currentHeight + 100) + 'px';

            if (btnInfo.type === 'image') {
                iframe.removeAttribute('src');
                iframe.srcdoc = `
                    <style>
                        body { 
                            margin: 0; 
                            background-color: #111; 
                            overflow-x: auto; 
                            overflow-y: hidden;
                            padding: 10px;
                        }
                        img { 
                            height: ${btnInfo.height - 20}px; // This will now be 630px (725-20)
                            width: auto; 
                            display: block;
                            border-radius: 4px;
                        }
                        /* Custom scrollbar for image view */
                        ::-webkit-scrollbar { 
                            width: 12px; 
                            height: 12px; 
                        }
                        ::-webkit-scrollbar-track { 
                            background: rgba(0, 0, 0, 0.8); 
                            border-radius: 6px; 
                            border: 1px solid #333; 
                        }
                        ::-webkit-scrollbar-thumb { 
                            background: linear-gradient(180deg, #333 0%, #222 50%, #111 100%); 
                            border-radius: 6px; 
                            border: 1px solid #444;
                            box-shadow: 
                                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                                0 0 8px rgba(184, 115, 51, 0.2);
                        }
                        ::-webkit-scrollbar-thumb:hover { 
                            background: linear-gradient(180deg, #444 0%, #333 50%, #222 100%);
                            border-color: #555;
                            box-shadow: 
                                inset 0 1px 0 rgba(255, 255, 255, 0.15),
                                0 0 12px rgba(184, 115, 51, 0.3);
                        }
                        ::-webkit-scrollbar-corner {
                            background: #000;
                        }
                        /* Firefox scrollbar */
                        body { 
                            scrollbar-width: thin; 
                            scrollbar-color: #333 #000; 
                        }
                    </style>
                    <body>
                        <img src="${btnInfo.src}" alt="Timeline Image" onload="parent.postMessage('imageLoaded', '*')">
                    </body>
                `;                // Hide loading overlay after image loads (with a small delay)
                setTimeout(() => {
                    hideLoadingOverlay(loadingOverlay);
                    // Setup external scrolling for new content
                    setupExternalScrolling(iframe, iframeWrapper);
                    // Re-initialize zoom for the new content
                    setTimeout(initializeZoom, 100);
                }, 800);} else {
                // Create a temporary iframe to measure the original HTML content
                const tempIframe = document.createElement('iframe');
                tempIframe.style.position = 'absolute';
                tempIframe.style.top = '-9999px';
                tempIframe.style.left = '-9999px';
                tempIframe.style.width = '100%';
                tempIframe.style.height = 'auto';
                tempIframe.style.border = 'none';
                tempIframe.src = btnInfo.src;
                
                document.body.appendChild(tempIframe);
                
                tempIframe.onload = () => {
                    let originalHeight = 1000; // Default fallback height
                    let originalWidth = 1400; // Default fallback width
                    
                    try {
                        // Try to get the actual content dimensions
                        const tempDoc = tempIframe.contentDocument || tempIframe.contentWindow.document;
                        if (tempDoc && tempDoc.body) {
                            originalHeight = Math.max(
                                tempDoc.body.scrollHeight,
                                tempDoc.body.offsetHeight,
                                tempDoc.documentElement.scrollHeight,
                                tempDoc.documentElement.offsetHeight
                            );
                            originalWidth = Math.max(
                                tempDoc.body.scrollWidth,
                                tempDoc.body.offsetWidth,
                                tempDoc.documentElement.scrollWidth,
                                tempDoc.documentElement.offsetWidth
                            );
                        }
                    } catch (e) {
                        // Cross-origin or other access issues, use default dimensions
                        console.log('Using default dimensions due to access restrictions');
                    }
                    
                    // Calculate scale factor to fit height to 700px
                    const targetHeight = btnInfo.height; // This will now use 725 from the button config
                    const scaleFactor = targetHeight / originalHeight;
                    const scaledWidth = originalWidth * scaleFactor;
                    
                    // Remove temporary iframe
                    document.body.removeChild(tempIframe);
                    
                    // Create the scaled HTML wrapper
                    iframe.removeAttribute('src');
                    iframe.srcdoc = `
                        <style>
                            body { 
                                margin: 0; 
                                background-color: #111; 
                                overflow-x: auto; 
                                overflow-y: hidden;
                                padding: 0;
                                height: ${targetHeight}px;
                                width: 100%;
                            }
                            .html-container {
                                transform-origin: top left;
                                transform: scale(${scaleFactor});
                                width: ${originalWidth}px;
                                height: ${originalHeight}px;
                            }
                            iframe.html-content {
                                width: 100%;
                                height: 100%;
                                border: none;
                                background: #111;
                            }
                            /* Enhanced scrollbar for HTML content */
                            ::-webkit-scrollbar { 
                                width: 20px; 
                                height: 20px; 
                            }
                            ::-webkit-scrollbar-track { 
                                background: rgba(0, 0, 0, 0.9); 
                                border-radius: 10px; 
                                border: 2px solid #333; 
                            }
                            ::-webkit-scrollbar-thumb { 
                                background: linear-gradient(180deg, #555 0%, #333 50%, #222 100%); 
                                border-radius: 10px; 
                                border: 2px solid #444;
                                box-shadow: 
                                    inset 0 2px 0 rgba(255, 255, 255, 0.1),
                                    0 0 15px rgba(184, 115, 51, 0.3);
                                min-height: 30px;
                            }
                            ::-webkit-scrollbar-thumb:hover { 
                                background: linear-gradient(180deg, #666 0%, #444 50%, #333 100%);
                                border-color: #555;
                                box-shadow: 
                                    inset 0 2px 0 rgba(255, 255, 255, 0.2),
                                    0 0 20px rgba(184, 115, 51, 0.4);
                            }
                            ::-webkit-scrollbar-thumb:active {
                                background: linear-gradient(180deg, #777 0%, #555 50%, #444 100%);
                                border-color: #666;
                            }
                            ::-webkit-scrollbar-corner {
                                background: #000;
                                border: 1px solid #333;
                            }
                            /* Firefox scrollbar */
                            body { 
                                scrollbar-width: thick; 
                                scrollbar-color: #555 #111; 
                            }
                        </style>
                        <body>
                            <div class="html-container">
                                <iframe class="html-content" src="${btnInfo.src}" onload="parent.postMessage('htmlLoaded', '*')"></iframe>
                            </div>
                        </body>
                    `;                    // Set up load event listener for HTML content
                    iframe.onload = () => {
                        // Add a small delay to ensure content is fully rendered
                        setTimeout(() => {
                            hideLoadingOverlay(loadingOverlay);
                            // Setup external scrolling for new content
                            setupExternalScrolling(iframe, iframeWrapper);
                            // Re-initialize zoom for the new content
                            setTimeout(initializeZoom, 100);
                        }, 500);
                    };
                };
            }
        });
        controlsContainer.appendChild(button);
    });

    vizContainer.insertBefore(controlsContainer, iframeWrapper);

    // Set first button as active by default and load its content
    if (controlsContainer.firstChild) {
        // On mobile, activate the Timeline Image button (second button)
        // On desktop, activate the Interactive Timeline button (first button)
        const defaultButton = isMobile() ? 
            controlsContainer.children[1] || controlsContainer.firstChild : 
            controlsContainer.firstChild;
            
        // Show loading overlay initially
        setTimeout(() => {
            showLoadingOverlay(loadingOverlay);
            defaultButton.click();
        }, 100);
    }

    syncThemeWithAnimation(controlsContainer);
}

// Function to show desktop-only message
function showDesktopOnlyMessage() {
    // Create modal overlay
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'desktop-only-modal-overlay';
    modalOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: modalFadeIn 0.3s ease-out;
    `;
    
    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'desktop-only-modal';
    modalContent.style.cssText = `
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #444;
        border-radius: 12px;
        padding: 30px;
        max-width: 400px;
        margin: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        animation: modalSlideIn 0.3s ease-out;
    `;
    
    modalContent.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 20px;">🔒</div>
        <h3 style="color: #fff; margin-bottom: 15px; font-family: 'JetBrains Mono', monospace;">Desktop Only Feature</h3>
        <p style="color: #ccc; margin-bottom: 25px; line-height: 1.5;">
            The Interactive Timeline requires a desktop browser for optimal performance and functionality. 
            Please switch to a desktop device to access this feature.
        </p>
        <button id="closeDesktopModal" style="
            background: linear-gradient(135deg, #444 0%, #333 100%);
            color: #fff;
            border: 2px solid #555;
            border-radius: 6px;
            padding: 12px 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        ">Got it</button>
    `;
    
    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);
    
    // Add close functionality
    const closeButton = modalContent.querySelector('#closeDesktopModal');
    const closeModal = () => {
        modalOverlay.style.animation = 'modalFadeOut 0.3s ease-out';
        setTimeout(() => {
            if (document.body.contains(modalOverlay)) {
                document.body.removeChild(modalOverlay);
            }
        }, 300);
    };
    
    closeButton.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
    
    // Close on escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
    
    // Add hover effect to button
    closeButton.addEventListener('mouseenter', () => {
        closeButton.style.background = 'linear-gradient(135deg, #555 0%, #444 100%)';
        closeButton.style.borderColor = '#666';
    });
    
    closeButton.addEventListener('mouseleave', () => {
        closeButton.style.background = 'linear-gradient(135deg, #444 0%, #333 100%)';
        closeButton.style.borderColor = '#555';
    });
}

function parseColor(str) {
    if (str.startsWith('#')) {
        const bigint = parseInt(str.substring(1), 16);
        return {
            r: (bigint >> 16) & 255,
            g: (bigint >> 8) & 255,
            b: bigint & 255,
            a: 1
        };
    } else if (str.startsWith('rgba')) {
        const parts = str.substring(5, str.length - 1).split(',').map(s => parseFloat(s.trim()));
        return { r: parts[0], g: parts[1], b: parts[2], a: parts[3] };
    } else if (str.startsWith('rgb')) {
        const parts = str.substring(4, str.length - 1).split(',').map(s => parseInt(s.trim(), 10));
        return { r: parts[0], g: parts[1], b: parts[2], a: 1 };
    }
    return { r: 0, g: 0, b: 0, a: 1 }; // Fallback
}

function interpolate(start, end, factor) {
    return start + (end - start) * factor;
}

function formatColor(color) {
    if (color.a < 1) {
        return `rgba(${Math.round(color.r)}, ${Math.round(color.g)}, ${Math.round(color.b)}, ${color.a.toFixed(3)})`;
    } else {
        const toHex = c => ('0' + Math.round(c).toString(16)).slice(-2);
        return `#${toHex(color.r)}${toHex(color.g)}${toHex(color.b)}`;
    }
}

function syncThemeWithAnimation(controlsContainer) {
    const timeMachineEffect = document.querySelector('.time-machine-effect');
    const godParticleEffect = document.querySelector('.god-particle-effect');

    if (!timeMachineEffect || !godParticleEffect) return;

    const themes = {
        bronze: {
            '--btn-text-color': '#cd853f',
            '--btn-border-color': '#b87333',
            '--btn-glow-color': 'rgba(184, 115, 51, 0.6)',
            '--btn-hover-bg': 'rgba(184, 115, 51, 0.2)',
            '--btn-hover-text-color': '#daa520',
            '--btn-active-bg': 'rgba(184, 115, 51, 0.4)',
            '--btn-active-text-color': '#ffd700',
            '--btn-active-border-color': '#daa520',
        },
        blue: {
            '--btn-text-color': '#add8e6',
            '--btn-border-color': '#4682b4',
            '--btn-glow-color': 'rgba(173, 216, 230, 0.6)',
            '--btn-hover-bg': 'rgba(173, 216, 230, 0.2)',
            '--btn-hover-text-color': '#e0ffff',
            '--btn-active-bg': 'rgba(173, 216, 230, 0.4)',
            '--btn-active-text-color': '#ffffff',
            '--btn-active-border-color': '#add8e6',
        }
    };

    const parsedThemes = {
        bronze: {},
        blue: {}
    };

    for (const key in themes.bronze) {
        parsedThemes.bronze[key] = parseColor(themes.bronze[key]);
        parsedThemes.blue[key] = parseColor(themes.blue[key]);
    }    // Variables to track transition timing
    let transitionStartTime = null;
    let currentTargetMixFactor = 0;
    let actualMixFactor = 0;
    const TRANSITION_DURATION = 10000; // 10 seconds in milliseconds

    setInterval(() => {
        const timeMachineOpacity = parseFloat(window.getComputedStyle(timeMachineEffect).opacity);
        const godParticleOpacity = parseFloat(window.getComputedStyle(godParticleEffect).opacity);

        const totalOpacity = timeMachineOpacity + godParticleOpacity;
        
        let targetMixFactor = 0;
        if (totalOpacity > 0.001) {
            // Calculate the raw mix factor
            const rawMixFactor = godParticleOpacity / totalOpacity;
            
            // Apply an extremely gradual transition with very slow color changes
            // The transition will be barely noticeable until very late in the cycle
            if (rawMixFactor < 0.6) {
                // Stay almost completely bronze for the first 60% with minimal hints
                targetMixFactor = Math.pow(rawMixFactor / 0.6, 3) * 0.08; // Cubic easing, max only 8%
            } else if (rawMixFactor < 0.85) {
                // Gradual increase from 60% to 85% of the cycle
                const midSection = (rawMixFactor - 0.6) / 0.25; // Normalize to 0-1
                targetMixFactor = 0.08 + (Math.pow(midSection, 2.5) * 0.22); // From 8% to 30%
            } else {
                // Final push to blue in the last 15% of the cycle
                const finalSection = (rawMixFactor - 0.85) / 0.15; // Normalize to 0-1
                targetMixFactor = 0.30 + (Math.pow(finalSection, 1.8) * 0.70); // From 30% to 100%
            }
        } else {
            targetMixFactor = 0; // Default to bronze when no animation is visible
        }

        // Check if target has changed significantly (more than 1% difference)
        if (Math.abs(targetMixFactor - currentTargetMixFactor) > 0.01) {
            currentTargetMixFactor = targetMixFactor;
            transitionStartTime = Date.now();
        }

        // Apply 4-second gradual transition to reach the target
        if (transitionStartTime !== null) {
            const elapsed = Date.now() - transitionStartTime;
            const progress = Math.min(elapsed / TRANSITION_DURATION, 1); // 0 to 1 over 4 seconds
            
            // Use smooth easing for the 4-second transition
            const easedProgress = progress < 0.5 
                ? 2 * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 3) / 2; // Smooth ease-in-out curve
            
            // Interpolate from current actual value to target over 4 seconds
            const startMixFactor = actualMixFactor;
            actualMixFactor = startMixFactor + (currentTargetMixFactor - startMixFactor) * easedProgress;
            
            // Reset transition when complete
            if (progress >= 1) {
                transitionStartTime = null;
            }
        } else {
            actualMixFactor = currentTargetMixFactor;
        }

        for (const key in parsedThemes.bronze) {
            const color1 = parsedThemes.bronze[key];
            const color2 = parsedThemes.blue[key];

            const mixedColor = {
                r: interpolate(color1.r, color2.r, actualMixFactor),
                g: interpolate(color1.g, color2.g, actualMixFactor),
                b: interpolate(color1.b, color2.b, actualMixFactor),
                a: interpolate(color1.a, color2.a, actualMixFactor)
            };

            controlsContainer.style.setProperty(key, formatColor(mixedColor));
        }
    }, 50); // Update colors ~20 times per second for a smooth transition
}

function addSmoothScrolling() {
    // Add smooth scrolling behavior to any internal links
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function optimizeAnimations() {
    // Use Intersection Observer to pause animations when not visible
    const animatedElements = document.querySelectorAll('.time-machine-effect, .god-particle-effect');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            } else {
                // Pause animations when not visible to improve performance
                entry.target.style.animationPlayState = 'paused';
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Dark theme slider enhancement
function applyDarkThemeToSliders() {
    // Wait for iframe to load
    const iframe = document.querySelector('.visualization-container iframe');
    if (!iframe) return;
    
    iframe.addEventListener('load', function() {
        try {
            // Try to access iframe content (may be blocked by CORS)
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            if (iframeDoc) {
                // Apply dark theme styles to any sliders found
                const sliders = iframeDoc.querySelectorAll('input[type="range"]');
                sliders.forEach(slider => {
                    slider.style.colorScheme = 'dark';
                });
                
                // Apply dark theme to Plotly slider components
                const plotlySliders = iframeDoc.querySelectorAll('.slider-container, .slider-group');
                plotlySliders.forEach(sliderContainer => {
                    sliderContainer.style.background = 'rgba(0, 0, 0, 0.8)';
                    sliderContainer.style.border = '1px solid #333';
                    sliderContainer.style.borderRadius = '8px';
                });
            }
        } catch (e) {
            // If CORS blocks access, styles from CSS will still apply
            console.log('Cross-origin iframe detected - using CSS-only dark theme');
        }
    });
}

// Enhanced smooth scrolling and transitions
function enhancePageTransitions() {
    const sections = document.querySelectorAll('.header-section, .visualization-container, .explanation-section');
    
    // Add intersection observer for smooth section transitions
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '-50px 0px'
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        sectionObserver.observe(section);
    });
    
    // Ensure header is always visible initially
    const header = document.querySelector('.header-section');
    if (header) {
        header.style.opacity = '1';
        header.style.transform = 'translateY(0)';
    }
}

// Enhanced iframe interaction
function enhanceIframeInteraction() {
    const iframe = document.querySelector('.visualization-container iframe');
    if (!iframe) return;
    
    // Apply custom scrollbar styles to iframe content
    iframe.addEventListener('load', function() {
        try {
            // Inject custom scrollbar CSS into the iframe
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            const style = iframeDoc.createElement('style');            style.textContent = `
                /* Eliminate white lines and backgrounds */
                * {
                    border: none !important;
                    outline: none !important;
                }
                
                html, body {
                    background: #111 !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border: none !important;
                    outline: none !important;
                }
                
                /* Custom Black Scrollbar for iframe content */
                ::-webkit-scrollbar {
                    width: 12px;
                    height: 12px;
                }
                
                ::-webkit-scrollbar-track {
                    background: #000;
                    border-radius: 6px;
                    border: 1px solid #333;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: linear-gradient(180deg, #333 0%, #222 50%, #111 100%);
                    border-radius: 6px;
                    border: 1px solid #444;
                    box-shadow: 
                        inset 0 1px 0 rgba(255, 255, 255, 0.1),
                        0 0 8px rgba(184, 115, 51, 0.2);
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: linear-gradient(180deg, #444 0%, #333 50%, #222 100%);
                    border-color: #555;
                    box-shadow: 
                        inset 0 1px 0 rgba(255, 255, 255, 0.15),
                        0 0 12px rgba(184, 115, 51, 0.3);
                }
                
                ::-webkit-scrollbar-thumb:active {
                    background: linear-gradient(180deg, #555 0%, #444 50%, #333 100%);
                    border-color: #666;
                }
                
                ::-webkit-scrollbar-corner {
                    background: #000;
                }
                
                /* Firefox scrollbar */
                html, body {
                    scrollbar-width: thin;
                    scrollbar-color: #333 #000;
                }
            `;
            
            iframeDoc.head.appendChild(style);
            console.log('Custom scrollbar styles injected into iframe');
        } catch (error) {
            console.log('Could not inject styles into iframe (likely due to CORS restrictions)');
            // Fallback: Apply styles to iframe container
            applyIframeContainerScrollbar();
        }
    });
    
    // Apply smooth hover effects
    iframe.addEventListener('mouseenter', function() {
        iframe.style.boxShadow = `
            0 0 40px rgba(184, 115, 51, 0.2),
            inset 0 0 25px rgba(0, 0, 0, 0.4)
        `;
    });
    
    iframe.addEventListener('mouseleave', function() {
        iframe.style.boxShadow = `
            0 0 30px rgba(184, 115, 51, 0.1),
            inset 0 0 20px rgba(0, 0, 0, 0.3)
        `;
    });
}

// Function to handle iframe content and external scrolling
function setupExternalScrolling(iframe, iframeWrapper) {
    if (!iframe || !iframeWrapper) return;
    
    iframe.addEventListener('load', function() {
        try {
            // Add class to wrapper to enable wide content scrolling
            iframeWrapper.classList.add('wide-content');
            
            // Ensure iframe takes full content width
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (iframeDoc && iframeDoc.body) {
                // Inject styles into iframe to disable internal scrollbars
                const style = iframeDoc.createElement('style');
                style.textContent = `
                    body, html {
                        overflow: visible !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        background: #111 !important;
                        width: auto !important;
                        height: auto !important;
                    }
                    * {
                        box-sizing: border-box !important;
                    }
                    ::-webkit-scrollbar {
                        display: none !important;
                    }
                `;
                iframeDoc.head.appendChild(style);
                
                // Get the actual content dimensions
                const contentWidth = Math.max(
                    iframeDoc.body.scrollWidth,
                    iframeDoc.body.offsetWidth,
                    iframeDoc.documentElement.scrollWidth,
                    iframeDoc.documentElement.offsetWidth
                );
                
                const contentHeight = Math.max(
                    iframeDoc.body.scrollHeight,
                    iframeDoc.body.offsetHeight,
                    iframeDoc.documentElement.scrollHeight,
                    iframeDoc.documentElement.offsetHeight
                );
                  // Set iframe dimensions to match content
                iframe.style.width = Math.max(contentWidth, 1400) + 'px';
                iframe.style.height = '725px'; // Fixed height as requested
                
                console.log(`Content dimensions: ${contentWidth}x${contentHeight}`);
            }
        } catch (e) {
            console.log('Cross-origin restrictions prevent iframe content modification');            // For cross-origin content, just ensure proper sizing
            iframe.style.width = '1500px'; // Default wide width to trigger scrolling
            iframe.style.height = '725px'; // Fixed height as requested
        }
    });
}

function applyIframeContainerScrollbar() {
    // Apply scrollbar styles to the visualization container
    const container = document.querySelector('.visualization-container');
    if (container) {
        container.style.overflow = 'auto';
    }
}

// Add header blackening effect on scroll
function addHeaderBlackeningEffect() {
    const header = document.querySelector('.header-section');
    if (!header) return;
    
    // Create overlay element for blackening effect
    const blackOverlay = document.createElement('div');
    blackOverlay.className = 'header-black-overlay';
    blackOverlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: #000;
        opacity: 0;
        transition: opacity 0.8s ease-out;
        pointer-events: none;
        z-index: 2;
    `;
    header.appendChild(blackOverlay);
    
    // Listen for scroll events
    window.addEventListener('scroll', function() {
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;
          // Calculate blackening progress (0 to 1)
        // Start blackening when scroll reaches 10% of viewport height (sooner)
        const blackenStartPoint = windowHeight * 0.1;
        const blackenEndPoint = windowHeight * 0.6;
        
        let blackenProgress = 0;
        
        if (scrollY >= blackenStartPoint) {
            if (scrollY >= blackenEndPoint) {
                blackenProgress = 1;
            } else {
                blackenProgress = (scrollY - blackenStartPoint) / (blackenEndPoint - blackenStartPoint);
            }
        }
        
        // Apply blackening effect (stronger darkness)
        blackOverlay.style.opacity = blackenProgress * 0.95; // Max 95% opacity for darker effect
        
        // Control the CSS pseudo-element opacity (stronger)
        header.style.setProperty('--blacken-opacity', blackenProgress * 0.9);
        
        // Also dim the animations as lights go out (more aggressive dimming)
        const animations = header.querySelectorAll('.background-animation, .time-machine-effect, .god-particle-effect');
        animations.forEach(animation => {
            animation.style.opacity = 1 - (blackenProgress * 0.85); // Dim more aggressively
        });
    });
}

// Loading overlay functions
// Dark TV Series quotes collection with character attributions
const darkQuotes = [
    { quote: "The question isn't how, the question is when.", character: "Claudia Tiedemann" },
    { quote: "We're not free in what we do because we're not free in what we want.", character: "The Stranger" },
    { quote: "What we know is a drop, what we don't know is an ocean.", character: "H.G. Tannhaus" },
    { quote: "Time is an illusion that helps things make sense.", character: "Jonas Kahnwald" },
    { quote: "The beginning is the end and the end is the beginning.", character: "Adam" },
    { quote: "We're perfect for each other. Never believe anything else.", character: "Jonas Kahnwald" },
    { quote: "Everything is connected.", character: "H.G. Tannhaus" },
    { quote: "What you've done, you've done for me.", character: "Martha Nielsen" },
    { quote: "The past influences the future, but the future also influences the past.", character: "Claudia Tiedemann" },
    { quote: "Life is a labyrinth. Some people spend their whole lives trying to find their way out.", character: "Mikkel Nielsen" },
    { quote: "Yesterday, today and tomorrow are not consecutive, they are connected in a never-ending circle.", character: "Claudia Tiedemann" },
    { quote: "We trust that time is linear. That it proceeds eternally, uniformly. Into infinity.", character: "The Stranger" },
    { quote: "But the distinction between past, present and future is only a stubbornly persistent illusion.", character: "H.G. Tannhaus" },
    { quote: "Every decision you've ever made has led to this moment.", character: "Adam" },
    { quote: "The snake bites its own tail.", character: "Noah" },
    { quote: "Sic mundus creatus est.", character: "Adam" },
    { quote: "Time travel is just visiting your memories.", character: "Charlotte Doppler" },
    { quote: "What is light without dark?", character: "Eva" },
    { quote: "We are wanderers in the fourth dimension.", character: "The Stranger" },
    { quote: "The cycle must be broken.", character: "Jonas Kahnwald" }
];

function getRandomQuote() {
    return darkQuotes[Math.floor(Math.random() * darkQuotes.length)];
}

function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: #111;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
        border-radius: 8px;
        overflow: hidden;
    `;
    
    // This will be populated by updateLoadingTheme
    overlay.innerHTML = '';
    
    return overlay;
}

function updateLoadingTheme(overlay) {
    // Determine current theme based on background animations
    const timeMachineEffect = document.querySelector('.time-machine-effect');
    const godParticleEffect = document.querySelector('.god-particle-effect');
    
    if (!timeMachineEffect || !godParticleEffect) return;
    
    const timeMachineOpacity = parseFloat(window.getComputedStyle(timeMachineEffect).opacity);
    const godParticleOpacity = parseFloat(window.getComputedStyle(godParticleEffect).opacity);
    
    // Determine which theme is more prominent
    const isTimeMachineTheme = timeMachineOpacity >= godParticleOpacity;
    
    if (isTimeMachineTheme) {
        createTimeMachineLoading(overlay);
    } else {
        createGodParticleLoading(overlay);
    }
}

function createTimeMachineLoading(overlay) {
    const randomQuote = getRandomQuote();
    
    overlay.innerHTML = `
        <div class="time-machine-background" style="
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at center, rgba(184, 115, 51, 0.1) 0%, rgba(139, 69, 19, 0.05) 50%, rgba(101, 67, 33, 0.1) 100%);
            animation: bronzeShimmer 6s ease-in-out infinite;
        "></div>
        
        <div class="loading-content" style="
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        ">
            <div class="copper-spinner-container" style="
                position: relative;
                width: 100px;
                height: 100px;
                margin-bottom: 30px;
            ">
                <div class="copper-outer-ring" style="
                    position: absolute;
                    width: 100px;
                    height: 100px;
                    border: 4px solid rgba(184, 115, 51, 0.3);
                    border-top: 4px solid #b87333;
                    border-radius: 50%;
                    animation: spin 2s linear infinite;
                    box-shadow: 0 0 30px rgba(184, 115, 51, 0.6);
                "></div>
                <div class="copper-inner-ring" style="
                    position: absolute;
                    width: 70px;
                    height: 70px;
                    top: 15px;
                    left: 15px;
                    border: 3px solid rgba(218, 165, 32, 0.4);
                    border-right: 3px solid #daa520;
                    border-radius: 50%;
                    animation: spin 1.5s linear infinite reverse;
                    box-shadow: 0 0 20px rgba(218, 165, 32, 0.4);
                "></div>
                <div class="copper-core" style="
                    position: absolute;
                    width: 30px;
                    height: 30px;
                    top: 35px;
                    left: 35px;
                    background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
                    border-radius: 50%;
                    animation: pulse 2s ease-in-out infinite;
                    box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
                "></div>
            </div>
            
            <div class="loading-text" style="
                color: #cd853f;
                font-family: 'JetBrains Mono', monospace;
                font-size: 16px;
                font-weight: 600;
                text-shadow: 0 0 15px rgba(205, 133, 63, 0.7);
                letter-spacing: 2px;
                animation: copperPulse 3s ease-in-out infinite;
                margin-bottom: 20px;
                text-align: center;
            ">LOADING TIMELINE...</div>
        </div>
        
        <div class="bronze-particles" style="
            position: absolute;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
        ">
            ${Array.from({length: 12}, (_, i) => `
                <div style="
                    position: absolute;
                    width: ${2 + Math.random() * 3}px;
                    height: ${2 + Math.random() * 3}px;
                    background: #cd853f;
                    border-radius: 50%;
                    opacity: 0.7;
                    animation: float-bronze-particle ${4 + Math.random() * 3}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 4}s;
                    left: ${20 + Math.random() * 60}%;
                    top: ${20 + Math.random() * 60}%;
                    box-shadow: 0 0 8px #cd853f;
                "></div>
            `).join('')}
        </div>
        
        <div class="loading-quote" style="
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            max-width: 85%;
            text-align: center;
            font-family: 'Crimson Text', serif;
            color: rgba(205, 133, 63, 0.9);
            text-shadow: 0 0 10px rgba(205, 133, 63, 0.4);
            animation: bronzeQuoteGlow 4s ease-in-out infinite;
            line-height: 1.5;
            padding: 0 20px;
        ">
            <div style="font-size: 15px; font-style: italic; margin-bottom: 8px;">
                "${randomQuote.quote}"
            </div>
            <div style="font-size: 12px; font-weight: 600; letter-spacing: 1px; opacity: 0.8;">
                — ${randomQuote.character}
            </div>
        </div>
    `;
}

function createGodParticleLoading(overlay) {
    const randomQuote = getRandomQuote();
    
    overlay.innerHTML = `
        <div class="god-particle-background" style="
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at center, rgba(173, 216, 230, 0.1) 0%, rgba(26, 26, 26, 0.15) 50%, rgba(0, 0, 0, 0.2) 100%);
            animation: blueShimmer 6s ease-in-out infinite;
        "></div>
        
        <div class="loading-content" style="
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        ">
            <div class="particle-spinner-container" style="
                position: relative;
                width: 90px;
                height: 90px;
                margin-bottom: 30px;
            ">
                <div class="particle-outer-ring" style="
                    position: absolute;
                    width: 90px;
                    height: 90px;
                    border: 3px solid rgba(173, 216, 230, 0.3);
                    border-top: 3px solid #add8e6;
                    border-left: 3px solid #87ceeb;
                    border-radius: 50%;
                    animation: spin 1.8s linear infinite;
                    box-shadow: 0 0 25px rgba(173, 216, 230, 0.6);
                "></div>
                <div class="particle-middle-ring" style="
                    position: absolute;
                    width: 60px;
                    height: 60px;
                    top: 15px;
                    left: 15px;
                    border: 2px solid rgba(135, 206, 235, 0.4);
                    border-bottom: 2px solid #87ceeb;
                    border-radius: 50%;
                    animation: spin 1.2s linear infinite reverse;
                    box-shadow: 0 0 15px rgba(135, 206, 235, 0.5);
                "></div>
                <div class="particle-core" style="
                    position: absolute;
                    width: 25px;
                    height: 25px;
                    top: 32.5px;
                    left: 32.5px;
                    background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, rgba(173, 216, 230, 0.2) 70%, transparent 100%);
                    border-radius: 50%;
                    animation: particlePulse 2.5s ease-in-out infinite;
                    box-shadow: 0 0 20px rgba(173, 216, 230, 0.8);
                "></div>
            </div>
            
            <div class="loading-text" style="
                color: #add8e6;
                font-family: 'JetBrains Mono', monospace;
                font-size: 16px;
                font-weight: 600;
                text-shadow: 0 0 15px rgba(173, 216, 230, 0.7);
                letter-spacing: 2px;
                animation: bluePulse 3s ease-in-out infinite;
                margin-bottom: 20px;
                text-align: center;
            ">LOADING TIMELINE...</div>
        </div>
        
        <div class="blue-particles" style="
            position: absolute;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
        ">
            ${Array.from({length: 10}, (_, i) => `
                <div style="
                    position: absolute;
                    width: ${1.5 + Math.random() * 2}px;
                    height: ${1.5 + Math.random() * 2}px;
                    background: #add8e6;
                    border-radius: 50%;
                    opacity: 0.8;
                    animation: float-blue-particle ${3 + Math.random() * 2}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 3}s;
                    left: ${25 + Math.random() * 50}%;
                    top: ${25 + Math.random() * 50}%;
                    box-shadow: 0 0 6px #add8e6;
                "></div>
            `).join('')}
            ${Array.from({length: 6}, (_, i) => `
                <div style="
                    position: absolute;
                    width: 1px;
                    height: ${10 + Math.random() * 15}px;
                    background: linear-gradient(to bottom, transparent, #add8e6, transparent);
                    opacity: 0.6;
                    animation: electricArc ${2 + Math.random() * 1.5}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 2}s;
                    left: ${30 + Math.random() * 40}%;
                    top: ${30 + Math.random() * 40}%;
                    transform-origin: center;
                    transform: rotate(${Math.random() * 360}deg);
                "></div>
            `).join('')}
        </div>
        
        <div class="loading-quote" style="
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            max-width: 85%;
            text-align: center;
            font-family: 'Crimson Text', serif;
            color: rgba(173, 216, 230, 0.9);
            text-shadow: 0 0 10px rgba(173, 216, 230, 0.4);
            animation: blueQuoteGlow 4s ease-in-out infinite;
            line-height: 1.5;
            padding: 0 20px;
        ">
            <div style="font-size: 15px; font-style: italic; margin-bottom: 8px;">
                "${randomQuote.quote}"
            </div>
            <div style="font-size: 12px; font-weight: 600; letter-spacing: 1px; opacity: 0.8;">
                — ${randomQuote.character}
            </div>
        </div>
    `;
}

function showLoadingOverlay(overlay) {
    // Update the loading theme based on current background animation
    updateLoadingTheme(overlay);
    
    overlay.style.opacity = '1';
    overlay.style.visibility = 'visible';
}

function hideLoadingOverlay(overlay) {
    overlay.style.opacity = '0';
    overlay.style.visibility = 'hidden';
}

// Listen for image load messages from iframe
window.addEventListener('message', function(event) {
    if (event.data === 'imageLoaded') {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            setTimeout(() => hideLoadingOverlay(loadingOverlay), 300);
        }
    }
});

// Additional utility functions for future enhancements
function getRandomPosition() {
    return {
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight
    };
}

function createGlowEffect(element) {
    if (!element) return;
    
    element.style.filter = 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.5))';
    element.style.transition = 'filter 0.3s ease';
}

// Handle window resize for responsive animations
window.addEventListener('resize', function() {
    // Recalculate animation positions for dynamic elements
    const dynamicSparks = document.querySelectorAll('.amber-spark[class*="spark-"]');
    dynamicSparks.forEach((spark, index) => {
        if (index >= 5) { // Only adjust dynamically created sparks
            const angle = (Math.random() * 360) * (Math.PI / 180);
            const radius = 90;
            const centerX = 100;
            const centerY = 100;
            
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            spark.style.top = y + 'px';
            spark.style.left = x + 'px';
            spark.style.transform = `rotate(${angle * (180 / Math.PI)}deg)`;
        }
    });
});

// Error handling for animation failures
window.addEventListener('error', function(e) {
    console.error('Animation error:', e.error);
    // Fallback: ensure basic functionality even if animations fail
    document.body.classList.add('animations-disabled');
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart);
        }, 0);
    });
}

// Zoom functionality (panning removed)
let zoomLevel = 1;
let zoomControlsTimeout = null;

function initializeZoom() {
    const vizContainer = document.querySelector('.visualization-container');
    let iframe = vizContainer.querySelector('iframe');
    
    if (!vizContainer || !iframe) {
        // Retry after a delay if elements aren't ready yet
        setTimeout(initializeZoom, 500);
        return;
    }

    // Remove any existing zoom elements to prevent duplication
    ['.zoom-controls', '.zoom-indicator', '.reset-btn'].forEach(selector => {
        const el = vizContainer.querySelector(selector);
        if (el) el.remove();
    });

    // Reset zoom state
    zoomLevel = 1;
    
    // Use the existing iframe-scroll-wrapper instead of creating a new one
    let iframeWrapper = vizContainer.querySelector('.iframe-scroll-wrapper');
    if (!iframeWrapper) {
        console.warn('iframe-scroll-wrapper not found, zoom functionality may not work properly');
        return;
    }
    
    // Create zoom controls
    const zoomControls = document.createElement('div');
    zoomControls.className = 'zoom-controls';
    
    const zoomInBtn = document.createElement('button');
    zoomInBtn.className = 'zoom-btn zoom-in';
    zoomInBtn.title = 'Zoom In';
    
    const zoomOutBtn = document.createElement('button');
    zoomOutBtn.className = 'zoom-btn zoom-out';
    zoomOutBtn.title = 'Zoom Out';
    
    zoomControls.appendChild(zoomInBtn);
    zoomControls.appendChild(zoomOutBtn);

    // Create zoom indicator
    const zoomIndicator = document.createElement('div');
    zoomIndicator.className = 'zoom-indicator';
    zoomIndicator.textContent = '100%';
    zoomIndicator.title = 'Zoom level. Scroll to zoom.';

    // Create reset button
    const resetBtn = document.createElement('button');
    resetBtn.className = 'reset-btn';
    resetBtn.textContent = 'Reset';
    resetBtn.title = 'Reset zoom (or double-click on frame border)';
    
    // --- MOBILE FIX: Always show and fix controls on mobile ---
    const isMobile = () => window.innerWidth <= 768 || /Mobi|Android/i.test(navigator.userAgent);
    if (isMobile()) {
        zoomControls.classList.add('mobile-fixed');
        zoomIndicator.classList.add('mobile-fixed');
        resetBtn.classList.add('mobile-fixed');
    }
    // --------------------------------------------------------

    // Add all controls to the visualization container to keep them fixed
    vizContainer.appendChild(zoomControls);
    vizContainer.appendChild(zoomIndicator);
    vizContainer.appendChild(resetBtn);
    
    // Zoom functionality
    zoomInBtn.addEventListener('click', () => {
        zoomIn(iframe, zoomIndicator);
    });
    zoomOutBtn.addEventListener('click', () => {
        zoomOut(iframe, zoomIndicator);
    });
    resetBtn.addEventListener('click', () => {
        resetView(iframe, zoomIndicator);
    });
    
    // Hover functionality for zoom controls - attached to vizContainer
    if (!isMobile()) {
        vizContainer.addEventListener('mouseenter', () => showZoomControls(zoomControls));
        vizContainer.addEventListener('mouseleave', () => hideZoomControlsDelayed(zoomControls));
        // Keep controls visible when hovering over them
        zoomControls.addEventListener('mouseenter', () => clearZoomControlsTimeout());
        zoomControls.addEventListener('mouseleave', () => hideZoomControlsDelayed(zoomControls));
    } else {
        // On mobile, always show controls
        zoomControls.classList.add('visible');
    }

    // Double-click to reset - on iframe itself
    iframe.addEventListener('dblclick', () => {
        resetView(iframe, zoomIndicator);
    });
    
    // Store references for other functions to use
    window.currentZoomIframe = iframe;
    window.currentZoomWrapper = iframeWrapper;
    window.currentZoomIndicator = zoomIndicator;
    window.currentZoomControls = zoomControls;
}

// Zoom control visibility functions
function showZoomControls(zoomControls) {
    clearZoomControlsTimeout();
    zoomControls.classList.add('visible');
}

function hideZoomControlsDelayed(zoomControls) {
    clearZoomControlsTimeout();
    zoomControlsTimeout = setTimeout(() => {
        zoomControls.classList.remove('visible');
    }, 3000); // Hide after 3 seconds
}

function clearZoomControlsTimeout() {
    if (zoomControlsTimeout) {
        clearTimeout(zoomControlsTimeout);
        zoomControlsTimeout = null;
    }
}

function zoomIn(iframe, indicator) {
    if (zoomLevel < 3) {
        zoomLevel += 0.2;
        updateTransform(iframe);
        updateZoomIndicator(indicator);
    }
}

function zoomOut(iframe, indicator) {
    if (zoomLevel > 0.5) {
        zoomLevel -= 0.2;
        updateTransform(iframe);
        updateZoomIndicator(indicator);
    }
}

function resetView(iframe, indicator) {
    zoomLevel = 1;
    updateTransform(iframe);
    updateZoomIndicator(indicator);
}

function updateTransform(iframe) {
    iframe.style.transform = `scale(${zoomLevel})`;
    iframe.style.transformOrigin = '0 0';
}

function updateZoomIndicator(indicator) {
    const zoomText = Math.round(zoomLevel * 100) + '%';
    indicator.textContent = zoomText;
}

// Handle window resize for mobile/desktop mode changes
window.addEventListener('resize', function() {
    // Debounce resize events
    clearTimeout(window.resizeTimeout);
    window.resizeTimeout = setTimeout(() => {
        // Check if we need to reinitialize controls due to mobile/desktop change
        const vizContainer = document.querySelector('.visualization-container');
        const controlsContainer = vizContainer?.querySelector('.viz-controls');
        
        if (controlsContainer) {
            // Remove existing controls and reinitialize
            controlsContainer.remove();
            initializeVizControls();
        }
    }, 250);
});



