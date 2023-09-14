var observeDOM = (function () {
    var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
    return function (obj, callback) {
        if (!obj || obj.nodeType !== 1) return; // validation
        if (MutationObserver) {
            // define a new observer
            var mutationObserver = new MutationObserver(callback)

            // have the observer observe for changes in children
            mutationObserver.observe(obj, { childList: true, subtree: true })
            return mutationObserver
        }
        // browser support fallback
        else if (window.addEventListener) {
            obj.addEventListener('DOMNodeInserted', callback, false)
            obj.addEventListener('DOMNodeRemoved', callback, false)
        }
    }
})();
// Do not edit below
class antiVandal {

    selector = "li[data-mw-revid],tr[data-mw-revid] td.mw-enhanced-rc-nested, table[data-mw-revid] tbody tr td.mw-changeslist-line-inner"
    oldidRegex = /oldid=(\d+)/
    init = function () {
        let o = document.querySelectorAll(this.selector);
        for (let i = 0; i < o.length; i++) {
            let e = o[i]
            let parent = e instanceof HTMLLIElement ? e : e.classList.contains("mw-enhanced-rc-nested") ? e.parentElement : e.parentElement.parentElement.parentElement
            if (e.dataset.antiVandal == '1') //already visited
                return;
            const diffElement = parent.querySelector('a.mw-changeslist-diff');
            var oldID = 0;
            if (diffElement) {
                const link = diffElement.href;
                oldID = link.match(this.oldidRegex)[1];
            }
            var goodButton = document.createElement("button"), badButton = document.createElement("button");
            goodButton.onclick = (e) => {
                this.push(oldID, parent.dataset.mwRevid, 1);
                e.target.style.background = 'grey';
                e.target.nextElementSibling.style.background = 'grey';
                e.target.nextElementSibling.onclick = function () { }
            }
            badButton.onclick = (e) => {
                this.push(oldID, parent.dataset.mwRevid, 0)
                e.target.style.background = 'grey';
                e.target.previousElementSibling.style.background = 'grey';
                e.target.previousElementSibling.onclick = function () { }
            }
            goodButton.innerHTML = 'Good'
            badButton.innerHTML = 'Bad'
            goodButton.style.color = 'green'
            badButton.style.color = 'red'
            goodButton.style.background = 'lime'
            badButton.style.background = 'pink'
            e.appendChild(goodButton);
            e.appendChild(badButton);
            e.dataset.antiVandal = '1';
        }
    }

    push = function (oldID, revid, label = 1) {
        label = 'label4antiVandal' + label;
        const content = localStorage.getItem(label) || '';
        const value = (content ? content + "," : "") + oldID + "," + revid;
        localStorage.setItem(label, value);
        console.log("pushing " + revid + " to " + label)
    }

    done = function (v) {
        localStorage.removeItem('label4antiVandal0')
        localStorage.removeItem('label4antiVandal1')
    }
    save = function () {
        var neg = localStorage.getItem('label4antiVandal0') || '',
            pos = localStorage.getItem('label4antiVandal1') || '';
        if (pos == '' && neg == '') {
            console.log('Nothing yet');
            return;
        }
        [neg, pos] = [
            [...new Set(neg.split(','))].map(v => v * 1), // negative
            [...new Set(pos.split(','))].map(v => 1 * v) //positive
        ];
        console.log(neg, pos)
        let data = {
            by: this.user,
            positive: pos,
            negative: neg
        }
        $.post({
            url: this.target,
            crossDomain: true,
            data: data,
            dataType: 'json',
            success: (d) => {
                console.log(d)
            }
        });
    }
    constructor() {
        this.user = mw.user.getId();
        this.target = "https://goodarticlebot.toolforge.org/sample/" + this.user;

        this.init = this.init.bind(this);
        this.save = this.save.bind(this);
        this.init();
        if (document.querySelector(this.selector)) {
            this.timer = setInterval(this.init, 5 * 1000);
            this.saver = setInterval(this.save, 60 * 1000);
        }
    }
}

var AntiVandal = new antiVandal();
console.log(AntiVandal);