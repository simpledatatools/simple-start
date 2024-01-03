window.addEventListener('DOMContentLoaded', event => {
    // Activate feather
    feather.replace();

    // Enable tooltips globally
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers globally
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Activate Bootstrap scrollspy for the sticky nav component
    const stickyNav = document.body.querySelector('#stickyNav');
    if (stickyNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#stickyNav',
            offset: 82,
        });
    }
    
    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
             document.body.classList.toggle('sidenav-toggled');
        }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sidenav-toggled'));
        });
    }

    // Close side navigation when width < LG
    const sidenavContent = document.body.querySelector('#layoutSidenav_content');
    if (sidenavContent) {

        sidenavContent.addEventListener('click', event => {
            const BOOTSTRAP_LG_WIDTH = 992;
            if (window.innerWidth >= 992) {
                return;
            }
            if (document.body.classList.contains("sidenav-toggled")) {
                document.body.classList.toggle("sidenav-toggled");
            }
        });
    }

    // Add active state to sidbar nav links
    let activatedPath = window.location.pathname.match(/([\w-]+\.html)/, '$1');

    if (activatedPath) {
        activatedPath = activatedPath[0];
    } else {
        activatedPath = 'index.html';
    }

    const targetAnchors = document.body.querySelectorAll('[href="' + activatedPath + '"].nav-link');

    targetAnchors.forEach(targetAnchor => {
        let parentNode = targetAnchor.parentNode;
        while (parentNode !== null && parentNode !== document.documentElement) {
            if (parentNode.classList.contains('collapse')) {
                parentNode.classList.add('show');
                const parentNavLink = document.body.querySelector(
                    '[data-bs-target="#' + parentNode.id + '"]'
                );
                parentNavLink.classList.remove('collapsed');
                parentNavLink.classList.add('active');
            }
            parentNode = parentNode.parentNode;
        }
        targetAnchor.classList.add('active');
    });
});

function loadImage(id, url) {
    const img = document.getElementById(id)
    if (img.getAttribute("data-onload-complete") == "false") {
        img.setAttribute('src', url)
        img.setAttribute("data-onload-complete", "true")
    }
}

const mediaViewerModal = new bootstrap.Modal(document.getElementById('media-viewer-modal'));
const mediaViewerCloseButton = document.getElementById('media-viewer-modal-close')
const mediaViewerImg = document.getElementById('media-viewer-img')
const mediaViewerVideo = document.getElementById('media-viewer-video')
const mediaViewerVideoSrc = document.getElementById('media-viewer-video-src')

function openMediaViewer(media_type, url, file_type=null) {
    if (media_type == 'image') {
        mediaViewerModal.show()
        mediaViewerImg.setAttribute('src', url)
        mediaViewerImg.classList.remove('d-none')
    }
    if (media_type == 'video') {
        mediaViewerModal.show()
        mediaViewerVideoSrc.setAttribute('src', url)
        mediaViewerVideoSrc.setAttribute('type', file_type)
        mediaViewerVideo.classList.remove('d-none')
    }
}

mediaViewerCloseButton.addEventListener('click', event => {
    mediaViewerModal.hide()
    mediaViewerImg.setAttribute('src', '')
    mediaViewerImg.classList.add('d-none')
    mediaViewerVideoSrc.setAttribute('src', '')
    mediaViewerVideoSrc.setAttribute('type', '')
    mediaViewerImg.classList.add('d-none')
    mediaViewerVideo.classList.add('d-none')
});

function downloadFile(url, name) {
    fetch(url)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        // Create a temporary URL for the blob
        const url = window.URL.createObjectURL(blob);
        // Create a link element
        const link = document.createElement('a');
        // Set the link's href attribute to the temporary URL
        link.href = url;
        // Set the link's download attribute to the desired filename
        link.download = name;
        // Simulate a click on the link to download the file
        document.body.appendChild(link);
        link.click();
        // Clean up the temporary URL
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}