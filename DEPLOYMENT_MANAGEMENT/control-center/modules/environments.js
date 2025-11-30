// ========================================
// מודול סביבות (Environments Module)
// ========================================

export async function init() {
    console.log('🌍 מאתחל מודול סביבות (Initializing Environments Module)');
    await renderEnvironments();
}

async function renderEnvironments() {
    const container = document.getElementById('environments');
    
    if (!container) {
        console.warn('⚠️ Environments container not found');
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Environments content will be rendered here
    console.log('✅ Environments module ready');
}
