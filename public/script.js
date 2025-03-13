(() => {
    const boxcontainer = document.querySelector('.container');
    const registerBtn = document.querySelector('.register-btn');
    const loginBtn = document.querySelector('.login-btn');
  
    registerBtn?.addEventListener('click', () => {
      boxcontainer.classList.add('active');
    });

    loginBtn?.addEventListener('click', () => {
        boxcontainer.classList.remove('active');
      });
  
  })();
  