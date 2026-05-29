function postHeight() {
  var h = document.documentElement.scrollHeight;
  parent.postMessage({ type: 'wrks:viz:resize', height: h }, '*');
}

function setupImageFullscreen() {
  var images = document.querySelectorAll('img.figure-media, .project-preview img, .image-strip img');
  if (!images.length) {
    return;
  }

  var overlay = document.createElement('div');
  overlay.className = 'image-fullscreen';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-hidden', 'true');

  var closeButton = document.createElement('button');
  closeButton.className = 'image-fullscreen-close';
  closeButton.type = 'button';
  closeButton.setAttribute('aria-label', 'Close full screen image');
  closeButton.textContent = 'x';

  var image = document.createElement('img');
  image.className = 'image-fullscreen-media';
  image.alt = '';

  overlay.appendChild(closeButton);
  overlay.appendChild(image);
  document.body.appendChild(overlay);

  function openImage(source) {
    image.src = source.currentSrc || source.src;
    image.alt = source.alt || '';
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('fullscreen-lock');
    closeButton.focus();
  }

  function closeImage() {
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('fullscreen-lock');
    image.removeAttribute('src');
  }

  images.forEach(function(img) {
    img.classList.add('is-fullscreenable');
    img.tabIndex = 0;
    img.addEventListener('click', function() {
      openImage(img);
    });
    img.addEventListener('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openImage(img);
      }
    });
  });

  closeButton.addEventListener('click', closeImage);
  overlay.addEventListener('click', function(event) {
    if (event.target === overlay) {
      closeImage();
    }
  });
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && overlay.classList.contains('is-open')) {
      closeImage();
    }
  });
}

window.addEventListener('load', postHeight);
window.addEventListener('resize', postHeight);
document.querySelectorAll('.tab-label').forEach(function(el) {
  el.addEventListener('click', function() {
    setTimeout(postHeight, 50);
  });
});
setupImageFullscreen();
