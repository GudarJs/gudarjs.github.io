import './workshop.css';

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.os-tabs').forEach(group => {
    const tabs   = group.querySelectorAll('.os-tab');
    const panels = group.querySelectorAll('.os-tab-panel');

    const activate = (idx) => {
      tabs.forEach((t, i)   => t.classList.toggle('is-active', i === idx));
      panels.forEach((p, i) => p.classList.toggle('is-active', i === idx));
    };

    tabs.forEach((tab, i) => tab.addEventListener('click', () => activate(i)));
  });
});
