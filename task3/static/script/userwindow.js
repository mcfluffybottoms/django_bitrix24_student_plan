BX24.init(
    function() {
        const links = document.querySelectorAll(".users");
        links.forEach(function(link) {
            link.onclick = function(e) {
                e.preventDefault();
                const userId = link.getAttribute('data-user-id') || '1';
                BX24.openPath("/company/personal/user/" + userId + "/",
                    function(result) {}
                );
            };
        });
    }
);