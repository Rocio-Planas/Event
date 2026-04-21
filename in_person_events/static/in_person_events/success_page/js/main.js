document.addEventListener('DOMContentLoaded', () => {
    console.log('Stratos Event Suite Success Page Loaded');
    
    const btn = document.querySelector('.btn-primary-custom');
    if (btn) {
        btn.addEventListener('click', () => {
            console.log('Redirecting to dashboard...');
            // In a real app, this would be: window.location.href = '/dashboard/';
        });
    }
});
