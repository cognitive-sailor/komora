// script.js
document.addEventListener('DOMContentLoaded', () => {
    const resizableBox = document.querySelector('.resizable-box');
    const handles = document.querySelectorAll('.resize-handle');
    const tooltip = document.getElementById('tooltip');

    handles.forEach(handle => {
        handle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            const handleClass = e.target.className.split(' ').pop();
            const startX = e.clientX;
            const startWidth = parseInt(window.getComputedStyle(resizableBox).width, 10);
            const startLeft = parseInt(window.getComputedStyle(resizableBox).left, 10);

            const onMouseMove = (e) => {
                let newWidth = startWidth;
                let newLeft = startLeft;

                if (handleClass === 'left') {
                    newWidth = Math.max(20, startWidth - (e.clientX - startX));
                    newLeft = startLeft + (startWidth - newWidth);
                    tooltip.style.left = `${e.clientX + 10}px`; // Position tooltip next to mouse
                    tooltip.style.top = `${e.clientY + 10}px`;
                    tooltip.innerText = `X: ${e.clientX}px`;
                    tooltip.style.display = 'block';
                } else if (handleClass === 'right') {
                    newWidth = Math.max(20, startWidth + (e.clientX - startX));
                    tooltip.style.left = `${e.clientX + 10}px`; // Position tooltip next to mouse
                    tooltip.style.top = `${e.clientY + 10}px`;
                    tooltip.innerText = `X: ${e.clientX}px`;
                    tooltip.style.display = 'block';
                }

                resizableBox.style.width = `${newWidth}px`;
                resizableBox.style.left = `${newLeft}px`;
            };

            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                tooltip.style.display = 'none'; // Hide tooltip on mouse up
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    });

    // Add functionality to move the rectangle
    let isDragging = false;
    let offsetX, offsetY;

    resizableBox.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('resize-handle')) return; // Ignore if clicking on a resize handle

        isDragging = true;
        offsetX = e.clientX - parseInt(window.getComputedStyle(resizableBox).left, 10);
        offsetY = e.clientY - parseInt(window.getComputedStyle(resizableBox).top, 10);

        const onMouseMove = (e) => {
            if (!isDragging) return;

            const newLeft = e.clientX - offsetX;
            const newTop = e.clientY - offsetY;

            resizableBox.style.left = `${newLeft}px`;
            resizableBox.style.top = `${newTop}px`;
            tooltip.style.left = `${e.clientX + 10}px`; // Position tooltip next to mouse
            tooltip.style.top = `${e.clientY + 10}px`;
            tooltip.innerText = `Start X: ${newLeft}px`;
            tooltip.style.display = 'block';
        };

        const onMouseUp = () => {
            isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            tooltip.style.display = 'none'; // Hide tooltip on mouse up
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });
});
