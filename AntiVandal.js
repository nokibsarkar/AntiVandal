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
    diffElementSelector = 'span.mw-changeslist-links a.mw-changeslist-diff,span.mw-changeslist-links a[title="পূর্বের সংস্করণের সাথে পার্থক্য"]'
    init = function () {
        let o = document.querySelectorAll(this.selector);
        for (let i = 0; i < o.length; i++) {
            let e = o[i]
            let parent = e instanceof HTMLLIElement ? e : e.classList.contains("mw-enhanced-rc-nested") ? e.parentElement : e.parentElement.parentElement.parentElement
            if (e.dataset.antiVandal == '1') //already visited
                return;
            
            var goodButton = document.createElement("button"), badButton = document.createElement("button");
            goodButton.onclick = (e) => {
                e.preventDefault()
                this.push(parent.dataset.mwRevid, 1);
                e.target.style.background = 'grey';
                e.target.nextElementSibling.style.background = 'grey';
                e.target.nextElementSibling.onclick = function () { }
            }
            badButton.onclick = (e) => {
                e.preventDefault()
                this.push(parent.dataset.mwRevid, 0)
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

    push = function (revid, label = 1) {
        label = 'label4antiVandal' + label;
        const content = localStorage.getItem(label) || '';
        const value = (content ? content + "," : "")  + revid;
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
            neg.split(',')?.filter(v => v != '').map(v => v * 1), // negative
            pos.split(',')?.filter(v => v != '').map(v => 1 * v) //positive
        ];
        let data = {
            by: this.user,
            positive: [...new Set(pos)],
            negative: [...new Set(neg)]
        }
        console.log(data)
        const done = this.done;
        $.post({
            url: this.target,
            crossDomain: true,
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: (d) => {
                console.log(d)
                done(d);
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