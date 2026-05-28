function postHeight() {
  var h = document.documentElement.scrollHeight;
  parent.postMessage({ type: 'wrks:viz:resize', height: h }, '*');
}
window.addEventListener('load', postHeight);
window.addEventListener('resize', postHeight);
document.querySelectorAll('.tab-label').forEach(function(el) {
  el.addEventListener('click', function() {
    setTimeout(postHeight, 50);
  });
});
