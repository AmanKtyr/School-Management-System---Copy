/**
 * Class-Section Filter Functionality
 * 
 * This script handles the dynamic filtering of sections based on selected class.
 * When a class is selected, it fetches only the sections from that class and 
 * updates the section dropdown accordingly.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all class filter dropdowns on the page
    const classFilters = document.querySelectorAll('[id$="-class-filter"], [id="class-filter"], [id="class"], [id="student_class"]');
    
    classFilters.forEach(classFilter => {
        if (!classFilter) return;
        
        // Find the corresponding section filter
        // Try different possible IDs based on naming conventions in the project
        let sectionFilterId;
        if (classFilter.id === 'class-filter') {
            sectionFilterId = 'section-filter';
        } else if (classFilter.id === 'class') {
            sectionFilterId = 'section';
        } else if (classFilter.id === 'student_class') {
            sectionFilterId = 'section';
        } else if (classFilter.id.endsWith('-class-filter')) {
            // Replace 'class-filter' with 'section-filter' in the ID
            sectionFilterId = classFilter.id.replace('class-filter', 'section-filter');
        }
        
        const sectionFilter = document.getElementById(sectionFilterId);
        if (!sectionFilter) return;
        
        // Add change event listener to class filter
        classFilter.addEventListener('change', function() {
            const classId = this.value;
            
            // Show loading indicator
            sectionFilter.innerHTML = '<option value="">Loading sections...</option>';
            
            if (classId) {
                // Fetch sections for this class
                fetch(`/api/get-sections/${classId}/`)
                    .then(response => response.json())
                    .then(data => {
                        // Reset dropdown with default option
                        sectionFilter.innerHTML = '<option value="">-- All Sections --</option>';
                        
                        // Add sections from this class only
                        if (data.sections && data.sections.length > 0) {
                            data.sections.forEach(section => {
                                const option = document.createElement('option');
                                option.value = section.id;
                                option.textContent = section.name;
                                sectionFilter.appendChild(option);
                            });
                        } else {
                            // If no sections found
                            const option = document.createElement('option');
                            option.disabled = true;
                            option.textContent = 'No sections found for this class';
                            sectionFilter.appendChild(option);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching sections:', error);
                        sectionFilter.innerHTML = '<option value="">-- All Sections --</option><option disabled>Error loading sections</option>';
                    });
            } else {
                // If no class selected, just show the default option
                sectionFilter.innerHTML = '<option value="">-- All Sections --</option>';
            }
        });
        
        // Trigger change event if class is already selected on page load
        if (classFilter.value) {
            classFilter.dispatchEvent(new Event('change'));
        }
    });
});
