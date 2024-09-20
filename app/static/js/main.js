document.addEventListener('DOMContentLoaded', (event) => {
    // 为所有的flash消息添加一个关闭按钮
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.classList.add('close');
        closeButton.addEventListener('click', () => {
            message.style.display = 'none';
        });
        message.appendChild(closeButton);
    });
});