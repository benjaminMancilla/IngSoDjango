// countDown.js
document.addEventListener('DOMContentLoaded', function() {
    function updateCountdown() {
        const countdownElements = document.querySelectorAll('.countdown');
        countdownElements.forEach(el => {
        const deadlineStr = el.getAttribute('data-deadline');
        const startDateStr = el.getAttribute('data-startdate');
    
        const deadline = new Date(deadlineStr);
        let startDate;
    
        // Si startDateStr no incluye tiempo, agregar hora predeterminada
        if (startDateStr.length <= 10) { // formato 'YYYY-MM-DD' tiene 10 caracteres
            // Agregar hora predeterminada (00:00:00) a startDate
            startDate = new Date(`${startDateStr}T00:00:00`);
        } else {
            startDate = new Date(startDateStr);
        }
    
        const now = new Date();
        const totalTime = deadline - startDate;
        const difference = deadline - now;
    
        const progressBar = el.closest('.card').querySelector('.progress-bar');
    
        if (difference > 0) {
            // Cálculo del tiempo restante
            const days = Math.floor(difference / (1000 * 60 * 60 * 24));
            const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((difference % (1000 * 60)) / 1000);
    
            el.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    
            // Actualizar la barra de progreso
            const timeElapsed = now - startDate;
            const percentage = (timeElapsed / totalTime) * 100;
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage.toFixed(2));
        } else {
            el.textContent = 'Plazo finalizado';
            progressBar.style.width = '100%';
            progressBar.classList.remove('bg-success');
            progressBar.classList.add('bg-danger');
        }
        });
    }
    
    // Actualizar cada segundo
    setInterval(updateCountdown, 1000);
    // Actualización inicial
    updateCountdown();
});
  
  
  