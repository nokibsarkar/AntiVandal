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
class AntiVandal2 {
    parentSelector = "li[data-mw-revid], table[data-mw-revid],tr.mw-changeslist-line,td.diff-ntitle,td.diff-otitle";
    revIDSelector = "[data-mw-revid]";
    undoSelector = 'span.mw-rollback-link,span.mw-history-undo,span.tw-rollback-link-vandalism';
    vandalismMessage = 'Do you think this is a vandalism?\nOk - Yes (Vandalism), Cancel - No';
    markAsVandalism = 'ধ্বংসপ্রবণতা';
    enabledColor = '#ff0808d4'
    disabledColor = 'rgb(137 75 75 / 83%)'
    target = '';
    user = '0';
    captureRollbacks() {
        console.info('captureRollbacks')
        const self = this;
        const revisions = document.querySelectorAll(self.parentSelector);
        [...revisions].forEach((revision) => {
            if (revision.dataset.antiVandal == '2') return;
            var revid = revision.dataset.mwRevid;
            if (!revid) {
                const revID = revision.querySelector(self.revIDSelector);
                if (revID) {
                    revid = revID.dataset.mwRevid;
                } else {
                    return;
                }
            }
            const takeFeedback = assumeVandalism => event => {
                if (assumeVandalism || confirm(self.vandalismMessage)) {
                    console.log('rollback clicked');
                    console.info(self.push(revid, 0));
                }
            }
            const rollBackButtons = revision.querySelectorAll(self.undoSelector);
            if (rollBackButtons.length > 0) {
                [...rollBackButtons].forEach((rollBackButton) => {
                    rollBackButton.onclick = takeFeedback(false);
                });
            } else {
                const MarkingButton = document.createElement('button');
                MarkingButton.innerHTML = self.markAsVandalism;
                MarkingButton.onclick = event => {
                    takeFeedback(true)(event);
                    event.target.style.background = self.disabledColor;
                    event.target.style.cursor = 'not-allowed';
                    event.target.innerText = 'ধ্বংসপ্রবণতা হিসাবে চিহ্নিত করা হয়েছে';
                    event.target.onclick = function () { alert('Already marked as vandalism') };
                }
                MarkingButton.style.color = 'white';
                MarkingButton.style.background = self.enabledColor;
                MarkingButton.style.border = 'none';
                MarkingButton.style.padding = '5px';
                MarkingButton.style.borderRadius = '10px';
                MarkingButton.style.margin = '3px';
                MarkingButton.style.cursor = 'pointer';
                revision.appendChild(MarkingButton);
            }
            revision.dataset.antiVandal = '2';

        });

    }
    push = function (revid, label = 1) {
        label = 'label4antiVandal' + label;
        var value = localStorage.getItem(label) ? localStorage.getItem(label) + ',' + revid : revid;
        localStorage.setItem(label, value);
        return "pushing " + revid + " to " + label;
    }

    done = function (v) {
        console.info("done", v)
        localStorage.removeItem('label4antiVandal0')
        localStorage.removeItem('label4antiVandal1')
    }
    save = function () {
        const self = this;
        var neg = localStorage.getItem('label4antiVandal0') || '',
            pos = localStorage.getItem('label4antiVandal1') || '';
        if (pos == '' && neg == '') {
            console.log('Nothing yet');
            return;
        }
        [neg, pos] = [
            [...new Set(neg.split(','))].map(v => v * 1).filter(v => v != 0), // negative
            [...new Set(pos.split(','))].map(v => 1 * v).filter(v => v != 0) //positive
        ];
        console.log(neg, pos)
        let data = {
            by: self.user,
            positive: pos,
            negative: neg
        }
        $.post({
            url: self.target,
            crossDomain: true,
            data: JSON.stringify(data),
            contentType : 'application/json',
            dataType: 'json',
            success: self.done
        });
    }
    constructor() {
        this.user = mw.user.getId();
        this.save = this.save.bind(this);
        this.target = "https://goodarticlebot.toolforge.org/sample/" + this.user;
        this.saver = setInterval(this.save, 60 * 1000);
        if (document.querySelector(this.parentSelector)) {
            this.captureRollbacks = this.captureRollbacks.bind(this);
            
            this.captureRollbacks();
            observeDOM(document.querySelector('#mw-content-text'), this.captureRollbacks);

            // this.timer = setInterval(this.init, 5 * 1000);
        }
    }
}
var antiVandal = new AntiVandal2();

// var AntiVandal = new antiVandal();
// console.log(AntiVandal);