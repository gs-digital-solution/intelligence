document.addEventListener('DOMContentLoaded', function() {
    // Sélecteurs communs
    const classeSelect = document.querySelector('.classe-select, #id_classe');
    const matiereSelect = document.querySelector('.matiere-select, #id_matiere');
    const typeExerciceSelect = document.getElementById('id_type_exercice');

    // Fonction générique pour charger les matières
    const loadMatieres = (classeId, targetSelect) => {
        if (classeId) {
            fetch(`/api/matieres/?classe_id=${classeId}`)
                .then(r => r.json())
                .then(data => {
                    let options = '<option value="">---------</option>';
                    if (data.matieres) { // Format de type_exercice_admin.js
                        data.matieres.forEach(m => {
                            options += `<option value="${m.id}">${m.nom}</option>`;
                        });
                    } else { // Format de exercice_admin.js original
                        options = data.options || '';
                    }
                    targetSelect.innerHTML = options;
                    
                    // Si on change la matière, on met à jour les types d'exercice
                    if (targetSelect === matiereSelect && typeExerciceSelect) {
                        updateTypeExercices(targetSelect.value);
                    }
                });
        } else {
            targetSelect.innerHTML = '<option value="">---------</option>';
        }
    };

    // Fonction pour charger les types d'exercice
    const updateTypeExercices = (matiereId) => {
        if (matiereId && typeExerciceSelect) {
            fetch(`/api/type-exercices/?matiere_id=${matiereId}`)
                .then(r => r.json())
                .then(data => {
                    let options = '<option value="">---------</option>';
                    data.forEach(item => {
                        options += `<option value="${item.id}">${item.nom}</option>`;
                    });
                    typeExerciceSelect.innerHTML = options;
                });
        } else if (typeExerciceSelect) {
            typeExerciceSelect.innerHTML = '<option value="">---------</option>';
        }
    };

    // Écouteurs d'événements
    if (classeSelect && matiereSelect) {
        classeSelect.addEventListener('change', function() {
            loadMatieres(this.value, matiereSelect);
        });
        
        // Initialisation si une classe est déjà sélectionnée
        if (classeSelect.value) {
            loadMatieres(classeSelect.value, matiereSelect);
        }
    }

    if (matiereSelect && typeExerciceSelect) {
        matiereSelect.addEventListener('change', function() {
            updateTypeExercices(this.value);
        });
        
        // Initialisation si une matière est déjà sélectionnée
        if (matiereSelect.value) {
            updateTypeExercices(matriceSelect.value);
        }
    }
});