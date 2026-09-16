       const cards = document.querySelectorAll('img');

        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left; 
                const y = e.clientY - rect.top;  

                const xPct = (x / rect.width) - 0.5;
                const yPct = (y / rect.height) - 0.5;

                const tiltIntensity = 30; 
                
                card.style.transform = `perspective(1000px) rotateY(${xPct * tiltIntensity}deg) rotateX(${-yPct * tiltIntensity}deg) scale3d(1.05, 1.05, 1.05)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = `perspective(1000px) rotateY(0deg) rotateX(0deg) scale3d(1, 1, 1)`;
            });
        });