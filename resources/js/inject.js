// --------------------------- 基础支持 ---------------------------

/**
 * 在元素上模拟鼠标按下事件
 * @param {string|HTMLElement} selector
 */
function pressMouseKey(selector) {
    let element = (selector instanceof HTMLElement) ? selector : document.querySelector(selector);
    if (element) {
        let clickEvent = document.createEvent('MouseEvent');
        clickEvent.initMouseEvent(
            'click',
            false,
            false,
            window,
            0,
            0,
            0,
            0,
            0,
            false,
            false,
            false,
            false,
            0,
            null
        );
        element.dispatchEvent(clickEvent);
        return true;
    }
    return false;
}

/**
 * 模拟发送键盘事件
 * @param {number} key_code
 */
function fireKeyEvent(key_code) {
    const ke = new KeyboardEvent('keydown', {
        bubbles: true, cancelable: true, keyCode: key_code
    });
    document.body.dispatchEvent(ke);
}

// --------------------------- 缓存数据 ---------------------------

const Action = {
    ScrollToEnd: 1,
    ReadingFinished: 2
}

const Cache = {
    HasSelection: false
}

// --------------------------- 选中状态 ---------------------------

/**
 * 监听选中状态
 */
function watchSelection() {
    const MutationObserver = window['MutationObserver'] || window['WebKitMutationObserver'] || window['MozMutationObserver']

    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'attributes') {
                Cache.HasSelection = mutation.target.style.display ? false : true;
                updateState(`选中状态改变 ${Cache.HasSelection}`);
            }
        });
    });

    const listen = (e) => {
        e && observer.observe(e, {
            attributes: true,
            // attributeFilter: ['style'],
            childList: true
        });
    }

    /**
     * 选中监听
     */
    function watch() {
        document.addEventListener('selectionchange', function () {
            let selection = window.getSelection()
            Cache.HasSelection = selection && selection.toString() !== '';
        })
        const element_toolbar = document.querySelector('.reader_toolbar_container');
        listen(element_toolbar);
    }

    // reader_toolbar_container 在加载后并未创建，因此先要监听他的父节点
    const element_container = document.querySelector('.renderTargetContainer');
    const observer_container = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            for (const node of mutation.addedNodes) {
                if (node.className === 'reader_toolbar_container') {
                    watch();
                    break;
                }
            }
        })
    });
    observer_container.observe(element_container, {
        childList: true,
    });

    const element_catalog = document.querySelector('.readerCatalog');
    const element_note = document.querySelector('.readerNotePanel');
    listen(element_catalog);
    listen(element_note);
}

// --------------------------- 自动滚动 ---------------------------

/**
 * 是否已滚动到底部
 */
function isScrollToEnd() {
    // 变量scrollTop是滚动条滚动时，滚动条上端距离顶部的距离
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    // 变量windowHeight是可视区的高度
    const windowHeight = document.documentElement.clientHeight || document.body.clientHeight;
    // 变量scrollHeight是滚动条的总高度（当前可滚动的页面的总高度）
    const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
    // 滚动条到底部
    return scrollTop + windowHeight >= scrollHeight;
}

/**
 * 滚动监听
 */
function watchScroll() {
    document.onscroll = function () {
        if (isScrollToEnd()) {
            sendAction(Action.ScrollToEnd);
        }
    };
}

/**
 * 切换下一章
 */
function nextChapter() {
    if (isPageLoading()) return;

    let element = document.querySelector('.readerFooter_button');
    if (element) {
        // 下一章: 按下向右按键（按键码39）
        updateState('正在切换下一章')
        fireKeyEvent(39);
    } else {
        // 找不到下一章时，查看全文是否已结束
        let done = document.querySelector('.readerFooter_ending');
        if (done) {
            updateState('全书完.');
            sendAction(Action.ReadingFinished);
            alert('全书完.')
        }
    }
    Cache.HasSelection = false;
}

/**
 * 页面是否正在加载中
 * @return {boolean}
 */
function isPageLoading() {
    return document.querySelector('.readerChapterContentLoading') ? true : false;
}

/**
 * 执行滚动
 * 调用此方法的间隔必须大于 16.7 ms
 */
function doScroll(offset_y = 0) {
    if (isPageLoading()) {
        updateState("页面加载中...");
        return;
    }

    if (Cache.HasSelection) {
        updateState("暂停");
        return;
    }

    if (isScrollToEnd()) {
        sendAction(Action.ScrollToEnd);
        return;
    }

    const top = (document.documentElement.scrollTop || document.body.scrollTop) + offset_y;
    scroll({left: 0, top: top, behavior: 'auto'});
    updateState(`自动阅读中...`);
}

window.onload = function () {
    watchScroll();
    watchSelection();
}
