// --------------------------- 基础支持 ---------------------------

// --------------------------- 缓存数据 ---------------------------

const Action = {
    ScrollToEnd: 1,
    ReadingFinished: 2
}

const Cache = {
    HasSelection: false,
    LastScrollToEndAt: 0
}

const SCROLL_END_THRESHOLD = 48;
const SCROLL_END_ACTION_COOLDOWN = 2500;

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
    if (element_container) {
        observer_container.observe(element_container, {
            childList: true,
        });
    }

    const element_catalog = document.querySelector('.readerCatalog');
    const element_note = document.querySelector('.readerNotePanel');
    listen(element_catalog);
    listen(element_note);
}

// --------------------------- 自动滚动 ---------------------------

/**
 * 页面滚动元素
 */
function getScrollElement() {
    return document.scrollingElement || document.documentElement || document.body;
}

/**
 * 当前滚动高度
 */
function getScrollTop() {
    const element = getScrollElement();
    return window.pageYOffset || element.scrollTop || document.documentElement.scrollTop || document.body.scrollTop || 0;
}

/**
 * 是否已滚动到底部
 */
function isScrollToEnd() {
    const element = getScrollElement();
    const scrollTop = getScrollTop();
    const windowHeight = window.innerHeight || element.clientHeight || document.documentElement.clientHeight || document.body.clientHeight || 0;
    const scrollHeight = Math.max(
        element.scrollHeight || 0,
        document.documentElement.scrollHeight || 0,
        document.body.scrollHeight || 0
    );
    return scrollTop + windowHeight >= scrollHeight - SCROLL_END_THRESHOLD;
}

/**
 * 防止到底时重复触发翻页
 */
function notifyScrollToEnd() {
    const now = Date.now();
    if (now - Cache.LastScrollToEndAt < SCROLL_END_ACTION_COOLDOWN) {
        return;
    }
    Cache.LastScrollToEndAt = now;
    if (isReadingFinished()) {
        notifyReadingFinished();
        return;
    }
    updateState('正在切换下一页');
    sendAction(Action.ScrollToEnd);
}

/**
 * 滚动监听
 */
function watchScroll() {
    document.onscroll = function () {
        if (isScrollToEnd()) {
            notifyScrollToEnd();
        }
    };
}

/**
 * 元素是否可见
 */
function isVisible(element) {
    if (!element) return false;
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
}

/**
 * 是否已经读完全书
 */
function isReadingFinished() {
    const done = document.querySelector('.readerFooter_ending, [class*="readerFooter"][class*="ending"], [class*="Ending"]');
    if (done && isVisible(done)) {
        return true;
    }

    const text = (document.body.innerText || '').slice(-1000);
    return ['全书完', '已读完', '阅读完', '没有更多'].some(function (keyword) {
        return text.indexOf(keyword) >= 0;
    });
}

/**
 * 通知 Python 全书已读完
 */
function notifyReadingFinished() {
    updateState('全书完.');
    sendAction(Action.ReadingFinished);
    alert('全书完.');
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
        notifyScrollToEnd();
        return;
    }

    const element = getScrollElement();
    const top = getScrollTop() + offset_y;
    if (element && element.scrollTo) {
        element.scrollTo({left: 0, top: top, behavior: 'auto'});
    } else {
        window.scrollTo({left: 0, top: top, behavior: 'auto'});
    }
    updateState(`自动阅读中...`);
}

window.onload = function () {
    watchScroll();
    watchSelection();
}
