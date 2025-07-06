document.addEventListener('DOMContentLoaded', function() {
    const classeSelect = document.getElementById('id_classe');
    const matiereSelect = document.getElementById('id_matiere');

    if (classeSelect && matiereSelect) {
        // 1. Filtrage des matières quand la classe change
        classeSelect.addEventListener('change', function() {
            const classeId = this.value;
            if (classeId) {
                fetch(`/admin/filter-matieres/?classe_id=${classeId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Réinitialise et remplit le select des matières
                        matiereSelect.innerHTML = '<option value="">---------</option>';
                        data.matieres.forEach(matiere => {
                            const option = document.createElement('option');
                            option.value = matiere.id;
                            option.textContent = matiere.nom;
                            matiereSelect.appendChild(option);
                        });
                        // Vide les leçons quand la classe change
                        resetLecons();
                    });
            } else {
                matiereSelect.innerHTML = '<option value="">---------</option>';
                resetLecons();
            }
        });

        // 2. Filtrage des leçons quand la matière change
        matiereSelect.addEventListener('change', function() {
            const matiereId = this.value;
            if (matiereId) {
                fetch(`/admin/filter-lecons/?matiere_id=${matiereId}`)
                    .then(response => response.json())
                    .then(populateLecons);
            } else {
                resetLecons();
            }
        });

        // Fonction pour vider les leçons
        function resetLecons() {
            const selectFrom = document.querySelector('select[name="lecons_from"]');
            if (selectFrom) selectFrom.innerHTML = '';
        }

        // Fonction pour remplir les leçons
        function populateLecons(data) {
            const selectFrom = document.querySelector('select[name="lecons_from"]');
            if (selectFrom) {
                selectFrom.innerHTML = '';
                data.lecons.forEach(lecon => {
                    const option = document.createElement('option');
                    option.value = lecon.id;
                    option.textContent = lecon.titre;
                    selectFrom.appendChild(option);
                });
            }
        }
    }
});