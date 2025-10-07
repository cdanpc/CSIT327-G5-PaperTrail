document.addEventListener('DOMContentLoaded', function() {
    
    // PART 1: Conditional Field Display
    const typeSelect = document.getElementById('id_resource_type'); 
    const fileContainer = document.getElementById('file-upload-container');
    const linkContainer = document.getElementById('link-upload-container');
    const fileGuidelines = document.getElementById('file-guidelines');
    const linkGuidelines = document.getElementById('link-guidelines');
    const initialGuidelines = document.getElementById('initial-guidelines');

    function toggleFields(selectedType) {
        fileContainer.style.display = 'none';
        linkContainer.style.display = 'none';
        fileGuidelines.style.display = 'none';
        linkGuidelines.style.display = 'none';
        initialGuidelines.style.display = 'block';

        if (selectedType === 'file') {
            fileContainer.style.display = 'block';
            fileGuidelines.style.display = 'block';
            initialGuidelines.style.display = 'none';
        } else if (selectedType === 'link') {
            linkContainer.style.display = 'block';
            linkGuidelines.style.display = 'block';
            initialGuidelines.style.display = 'none';
        }
    }
    
    if (typeSelect) {
        toggleFields(typeSelect.value);
        typeSelect.addEventListener('change', function() {
            toggleFields(this.value);
        });
    }

    // PART 2: Client-Side Dynamic Formset Logic (Related Resources)
    const formsetContainer = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form-btn');
    const totalFormsInput = document.querySelector('[name="related_links-TOTAL_FORMS"]'); 
    
    let emptyFormTemplate = null;

    function updateFormIndex(element, index) {
        const prefix = 'related_links';
        const nameRegex = new RegExp(`${prefix}-\\d+`, 'g'); 
        
        ['name', 'id', 'htmlFor'].forEach(attr => {
            if (element.hasAttribute(attr)) {
                let currentValue = element.getAttribute(attr);
                if (currentValue) {
                    element.setAttribute(attr, currentValue.replace(nameRegex, `${prefix}-${index}`));
                }
            }
        });
    }
    
    function reIndexForms() {
        const forms = formsetContainer.querySelectorAll('.related-link-form');
        let formIndex = 0;      
        let visibleCount = 0;   
        
        forms.forEach((form) => {
            if (form.id === 'empty-form-template') return; 

            const deleteCheckbox = form.querySelector('input[name$="-DELETE"]');
            
            const isVisible = form.style.display !== 'none' && (!deleteCheckbox || !deleteCheckbox.checked);

            form.querySelectorAll('[name^="related_links-"], [id^="id_related_links-"], label[for^="id_related_links-"]').forEach(element => {
                updateFormIndex(element, formIndex);
            });
            
            if (isVisible) {
                let header = form.querySelector('h6.text-primary');
                if (header) {
                    header.textContent = `Link #${visibleCount + 1}`;
                }
                visibleCount++;
            }
            formIndex++; 
        });
        
        totalFormsInput.value = formIndex; 
    }

    function deleteForm(e) {
        e.preventDefault();
        const formToDelete = e.target.closest('.related-link-form');
        if (!formToDelete || formToDelete.id === 'empty-form-template') return;

        const pkInput = formToDelete.querySelector('input[name$="-id"]');
        const deleteCheckbox = formToDelete.querySelector('input[name$="-DELETE"]');

        if (deleteCheckbox && pkInput && pkInput.value) {
            deleteCheckbox.checked = true;
            formToDelete.style.display = 'none';
        } else {
            formToDelete.remove();
        }
        
        reIndexForms(); 
    }
    
    function attachDeleteHandler(form) {
        const deleteButton = form.querySelector('.remove-form-btn');
        if (deleteButton) {
            deleteButton.removeEventListener('click', deleteForm);
            deleteButton.addEventListener('click', deleteForm);
        }
    }
    
    function addForm(e) {
        e.preventDefault();
        if (!emptyFormTemplate) return;
    
        let currentFormCount = parseInt(totalFormsInput.value);
        const newForm = emptyFormTemplate.cloneNode(true);
        
        newForm.style.display = 'block';
        newForm.id = `related-form-${currentFormCount}`;
        
        // CRITICAL FIX: Only index elements with the related_links prefix
        // when setting up the new form. This prevents polluting the Tags field.
        newForm.querySelectorAll('[name^="related_links-"], [id^="id_related_links-"], label[for^="id_related_links-"]').forEach(element => {
            updateFormIndex(element, currentFormCount);
            
            // This part is crucial for new forms: reset the PK
            if (element.name && element.name.endsWith('-id')) {
                element.value = '';
            }
        });
    
        formsetContainer.appendChild(newForm);
        totalFormsInput.value = currentFormCount + 1; 
        
        attachDeleteHandler(newForm);
        
        // Global re-index to confirm numbering and total forms count
        reIndexForms();
    }

    // Initialization
    const currentForms = formsetContainer.querySelectorAll('.related-link-form');
    
    // Create and hide the empty form template for cloning
    if (currentForms.length > 0) {
        const lastForm = currentForms[currentForms.length - 1]; 
        
        emptyFormTemplate = lastForm.cloneNode(true);
        
        emptyFormTemplate.querySelectorAll('input, select, textarea').forEach(element => {
            if (element.type !== 'hidden' && element.type !== 'checkbox') {
                element.value = '';
            }
            if (element.name && element.name.endsWith('-DELETE')) {
                element.checked = false;
            }
            if (element.name && element.name.endsWith('-id')) {
                element.value = '';
            }
        });
        
        emptyFormTemplate.style.display = 'none';
        emptyFormTemplate.id = 'empty-form-template';
        
        formsetContainer.appendChild(emptyFormTemplate);
    }
    
    // Hide initial empty form(s) and attach handlers
    currentForms.forEach((form) => {
        const pkInput = form.querySelector('input[name$="-id"]');
        
        if (!pkInput || !pkInput.value) {
            form.style.display = 'none';
        }
        
        attachDeleteHandler(form);
    });
    
    reIndexForms();

    if (addButton) {
        addButton.addEventListener('click', addForm);
    }
});