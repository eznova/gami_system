const backendUrl = `${window.location.protocol}//${window.location.hostname}:5000`
console.log(backendUrl)

window.onload = function() {
    const selectedId = localStorage.getItem('selectedNav');
    if (selectedId) {
        selectNavItem(document.getElementById(selectedId));
    } else {
        selectNavItem(document.getElementById('my-page'));
    }
};

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        selectNavItem(item);
        localStorage.setItem('selectedNav', item.id);
    });
});

function selectNavItem(selectedItem) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('selected');
        const icon = item.querySelector('.nav-icon');
        icon.src = item.dataset.iconDefault;
    });

    selectedItem.classList.add('selected');
    const selectedIcon = selectedItem.querySelector('.nav-icon');
    selectedIcon.src = selectedItem.dataset.iconSelected;

    const content = document.getElementById('content');

    if (selectedItem.id === 'my-page') {
        fetch('subpages/my-page.html')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка загрузки шаблона');
                }
                return response.text();
            })
            .then(template => {
                const userId = 4; // Замените на реальный user_id

                return Promise.all([
                    fetch(`${backendUrl}/users/get/${userId}/personal`).then(res => res.json()),
                    fetch(`${backendUrl}/users/get/${userId}/photo`).then(res => res.json()),
                    fetch(`${backendUrl}/users/get/${userId}/job_info`).then(res => res.json()),
                    fetch(`${backendUrl}/users/get/${userId}/details`).then(res => res.json())
                ])
                .then(([personalData, photoData, jobInfoData, detailsData]) => {
                    const jobTitle = jobInfoData.job_titles[0]?.title || '';
                    const department = jobInfoData.job_titles[0]?.department || '';
                    const role = jobInfoData.job_titles[0]?.role || '';
                    
                    // if photoData.photo is null, set it to svg tag icon
                    if (photoData.photo === "") {
                        photoData.photo = {
                            src: 'imgs/default_photo.svg',
                        }
                    }
                    else {
                        photoData.photo = {
                            src: photoData.photo,
                        }
                    }
                    const data = {
                        ...personalData,
                        photo: photoData.photo.src,
                        job_title: jobTitle,
                        department: department,
                        role: role,
                        interests: detailsData.interests,
                        ncoins: detailsData.ncoins,
                        thanks_count: detailsData.thanks_count,
                        rating: detailsData.rating,
                    };
                    // print debug message to console

                    const filledTemplate = template.replace(/{{(.*?)}}/g, (_, key) => {
                        return data[key.trim()] || '';
                    });

                    content.innerHTML = filledTemplate;
                });
            })
            .catch(error => {
                content.innerHTML = `<p class="text-danger">Ошибка: ${error.message}</p>`;
            });
    } else {
        content.textContent = `Раздел "${selectedItem.dataset.title}" еще в разработке`;
    }
}
