package com.example.demo.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResponse<T> {
    private Long total;
    private Integer page;
    private Integer size;
    private Integer totalPages;
    private List<T> data;

    public static <T> PageResponse<T> of(Long total, Integer page, Integer size, List<T> data) {
        int totalPages = (int) Math.ceil((double) total / size);
        return PageResponse.<T>builder()
                .total(total)
                .page(page)
                .size(size)
                .totalPages(totalPages)
                .data(data)
                .build();
    }
}
